// -----------------------------------------------------------------------------
// zephyr_coss_csr.sv  — AXI4-Lite CSR register file for the Zephyr COSS.
//
// Implements the register map in MAS §3. All registers are 32-bit, word-aligned.
//
// Deliberate demo drifts vs. the MAS:
//   [0.8] PERF_MISS (0x034) is NOT implemented                    -> MISSING
//   INT_STATUS sits at 0x058 (relocated by the Sep-02 design review, not the
//     MAS's 0x054) — the RTL follows the review (see the decisions layer).
//   DBG_SCRATCH (0x070) is undocumented in the MAS — a temporary bring-up hook
//     flagged in an Aug-20 meeting note.
// -----------------------------------------------------------------------------
module zephyr_coss_csr (
    input  wire        aclk,
    input  wire        aresetn,

    input  wire [11:0] s_axi_awaddr,
    input  wire        s_axi_awvalid,
    output wire        s_axi_awready,
    input  wire [31:0] s_axi_wdata,
    input  wire        s_axi_wvalid,
    output wire        s_axi_wready,
    input  wire [11:0] s_axi_araddr,
    input  wire        s_axi_arvalid,
    output wire        s_axi_arready,
    output reg  [31:0] s_axi_rdata,
    output wire        s_axi_rvalid,

    output wire        job_start,
    input  wire        job_done,
    input  wire        job_error,
    input  wire        cache_hit,
    input  wire        cache_miss,
    input  wire [2:0]  arb_grant,
    output wire        irq,
    input  wire        scan_en
);

    // ---- CSR byte-offset address map (MAS §3) ----
    localparam ADDR_CTRL           = 12'h000;  // §3.1
    localparam ADDR_CFG            = 12'h004;
    localparam ADDR_STATUS         = 12'h008;
    localparam ADDR_RING_BASE      = 12'h010;  // §3.2
    localparam ADDR_RING_HEAD      = 12'h014;
    localparam ADDR_RING_TAIL      = 12'h018;
    localparam ADDR_RING_SIZE      = 12'h01C;
    localparam ADDR_PERF_BYTES_IN  = 12'h020;  // §3.3
    localparam ADDR_PERF_BYTES_OUT = 12'h024;
    localparam ADDR_PERF_JOBS      = 12'h028;
    localparam ADDR_PERF_CYCLES    = 12'h02C;
    localparam ADDR_PERF_HITS      = 12'h030;
    // NOTE: no ADDR_PERF_MISS (0x034) -> PERF_MISS is MISSING (MAS §3.3)
    localparam ADDR_ARB_GRANTS     = 12'h038;
    localparam ADDR_ERROR          = 12'h040;  // §3.4
    localparam ADDR_ERR_ADDR       = 12'h044;
    localparam ADDR_ERR_INFO       = 12'h048;
    localparam ADDR_INT_EN         = 12'h050;  // §3.5
    localparam ADDR_INT_STATUS     = 12'h058;  // relocated by design review
    localparam ADDR_DBG_CTRL       = 12'h060;  // §3.6
    localparam ADDR_DBG_STATE      = 12'h064;
    localparam ADDR_DBG_OBS_SEL    = 12'h068;
    localparam ADDR_DBG_TRACE      = 12'h06C;
    localparam ADDR_DBG_SCRATCH    = 12'h070;  // UNDOCUMENTED temporary hook

    // ---- Register storage ----
    reg [31:0] ctrl_reg, cfg_reg, status_reg;
    reg [31:0] ring_base_reg, ring_head_reg, ring_tail_reg, ring_size_reg;
    reg [31:0] perf_bytes_in_reg, perf_bytes_out_reg, perf_jobs_reg;
    reg [31:0] perf_cycles_reg, perf_hits_reg, arb_grants_reg;
    reg [31:0] error_reg, err_addr_reg, err_info_reg;
    reg [31:0] int_en_reg, int_status_reg;
    reg [31:0] dbg_ctrl_reg, dbg_state_reg, dbg_obs_sel_reg, dbg_trace_reg;
    reg [31:0] dbg_scratch_reg;

    wire wr = s_axi_awvalid & s_axi_wvalid;

    // ---- Write path ----
    always_ff @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            ctrl_reg       <= 32'h0;
            cfg_reg        <= 32'h0;
            ring_base_reg  <= 32'h0;
            ring_tail_reg  <= 32'h0;
            ring_size_reg  <= 32'h0;
            int_en_reg     <= 32'h0;
            int_status_reg <= 32'h0;
            error_reg      <= 32'h0;
            dbg_ctrl_reg   <= 32'h0;
            dbg_obs_sel_reg<= 32'h0;
            dbg_scratch_reg<= 32'h0;
        end else begin
            // START doorbell auto-clears
            if (ctrl_reg[0]) ctrl_reg[0] <= 1'b0;
            if (wr) begin
                case (s_axi_awaddr)
                    ADDR_CTRL:        ctrl_reg        <= s_axi_wdata;
                    ADDR_CFG:         cfg_reg         <= s_axi_wdata;
                    ADDR_RING_BASE:   ring_base_reg   <= s_axi_wdata;
                    ADDR_RING_TAIL:   ring_tail_reg   <= s_axi_wdata;
                    ADDR_RING_SIZE:   ring_size_reg   <= s_axi_wdata;
                    ADDR_INT_EN:      int_en_reg      <= s_axi_wdata;
                    ADDR_INT_STATUS:  int_status_reg  <= int_status_reg & ~s_axi_wdata; // W1C
                    ADDR_ERROR:       error_reg       <= error_reg & ~s_axi_wdata;      // W1C
                    ADDR_DBG_CTRL:    dbg_ctrl_reg    <= s_axi_wdata;
                    ADDR_DBG_OBS_SEL: dbg_obs_sel_reg <= s_axi_wdata;
                    ADDR_DBG_SCRATCH: dbg_scratch_reg <= s_axi_wdata;
                    default:          /* read-only or reserved */ ;
                endcase
            end
            if (job_error) error_reg[0] <= 1'b1;
            if (job_done)  int_status_reg[0] <= 1'b1;
        end
    end

    // ---- Performance / status shadow ----
    always_ff @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            perf_jobs_reg <= 32'h0; perf_hits_reg <= 32'h0;
            arb_grants_reg <= 32'h0; status_reg <= 32'h1;
        end else begin
            if (job_done)  perf_jobs_reg <= perf_jobs_reg + 1'b1;
            if (cache_hit) perf_hits_reg <= perf_hits_reg + 1'b1;
            arb_grants_reg <= arb_grants_reg + arb_grant;
            status_reg     <= {29'h0, job_error, job_done, 1'b0};
        end
    end

    // ---- Read path ----
    always_comb begin
        case (s_axi_araddr)
            ADDR_CTRL:        s_axi_rdata = ctrl_reg;
            ADDR_CFG:         s_axi_rdata = cfg_reg;
            ADDR_STATUS:      s_axi_rdata = status_reg;
            ADDR_RING_HEAD:   s_axi_rdata = ring_head_reg;
            ADDR_PERF_JOBS:   s_axi_rdata = perf_jobs_reg;
            ADDR_PERF_HITS:   s_axi_rdata = perf_hits_reg;
            ADDR_ARB_GRANTS:  s_axi_rdata = arb_grants_reg;
            ADDR_ERROR:       s_axi_rdata = error_reg;
            ADDR_INT_STATUS:  s_axi_rdata = int_status_reg;
            ADDR_DBG_STATE:   s_axi_rdata = dbg_state_reg;
            default:          s_axi_rdata = 32'h0;
        endcase
    end

    assign s_axi_awready = 1'b1;
    assign s_axi_wready  = 1'b1;
    assign s_axi_arready = 1'b1;
    assign s_axi_rvalid  = 1'b1;
    assign job_start     = ctrl_reg[0];
    assign irq           = int_status_reg[0] & int_en_reg[0];

endmodule
