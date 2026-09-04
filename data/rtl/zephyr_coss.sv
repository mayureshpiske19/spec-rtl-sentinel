// -----------------------------------------------------------------------------
// zephyr_coss.sv  (SYNTHETIC RTL for the Spec-RTL Sentinel demo)
//
// Implements the Zephyr LZ Compression Offload Sub-System (COSS) control plane:
// the AXI4-Lite CSR register file and the job-sequencer FSM, per zephyr_coss_mas.md.
//
// The implementation is faithful to the MAS EXCEPT for a few deliberate drifts
// so Sentinel has something to catch, spread across maturity milestones:
//   [0.1] m_axi_wdata is 32-bit; MAS §2.1 requires 64-bit        -> WIDTH DRIFT
//   [0.5] control_fsm is missing the WRITE_OUT state (MAS §4.1)   -> MISSING
//   [0.8] PERF_MISS register (MAS §3.3) is not implemented        -> MISSING
//
// Also present (handled by the design-intent layer, not bugs):
//   INT_STATUS sits at 0x058, not the MAS's 0x054 — a later design review
//     relocated it; the RTL follows the review (see the decisions layer).
//   DBG_SCRATCH at 0x070 is undocumented in the MAS — a known temporary debug
//     hook flagged in a meeting note.
// -----------------------------------------------------------------------------
module zephyr_coss #(
    parameter int ADDR_WIDTH = 12,
    parameter int DATA_WIDTH = 64
) (
    input  wire        aclk,
    input  wire        aresetn,          // active-low async-assert/sync-release

    // ---- AXI4-Lite CSR subordinate (firmware register access) ----
    input  wire [11:0] s_axi_awaddr,     // 12-bit CSR address (MAS §2.3)
    input  wire        s_axi_awvalid,
    output wire        s_axi_awready,
    input  wire [31:0] s_axi_wdata,
    input  wire        s_axi_wvalid,
    output wire        s_axi_wready,
    input  wire [11:0] s_axi_araddr,
    input  wire        s_axi_arvalid,
    output wire        s_axi_arready,
    output wire [31:0] s_axi_rdata,
    output wire        s_axi_rvalid,

    // ---- AXI4 memory master (accelerator datapath) ----
    output wire [31:0] m_axi_wdata,      // DRIFT: MAS §2.1 requires 64-bit
    output wire        m_axi_wvalid,
    input  wire        m_axi_wready,

    // ---- Interrupt + DFT ----
    output wire        irq,
    input  wire        scan_en           // scan-based DFT enable (MAS §5.1)
);

    // ---- CSR address map (byte offsets from the CSR base) ----
    localparam ADDR_CTRL           = 12'h000;  // MAS §3.1
    localparam ADDR_CFG            = 12'h004;
    localparam ADDR_STATUS         = 12'h008;
    localparam ADDR_RING_BASE      = 12'h010;  // MAS §3.2
    localparam ADDR_RING_HEAD      = 12'h014;
    localparam ADDR_RING_TAIL      = 12'h018;
    localparam ADDR_RING_SIZE      = 12'h01C;
    localparam ADDR_PERF_BYTES_IN  = 12'h020;  // MAS §3.3
    localparam ADDR_PERF_BYTES_OUT = 12'h024;
    localparam ADDR_PERF_JOBS      = 12'h028;
    localparam ADDR_PERF_CYCLES    = 12'h02C;
    localparam ADDR_PERF_HITS      = 12'h030;
    // NOTE: no ADDR_PERF_MISS (0x034) -> PERF_MISS is MISSING (MAS §3.3)
    localparam ADDR_ARB_GRANTS     = 12'h038;
    localparam ADDR_ERROR          = 12'h040;  // MAS §3.4
    localparam ADDR_ERR_ADDR       = 12'h044;
    localparam ADDR_ERR_INFO       = 12'h048;
    localparam ADDR_INT_EN         = 12'h050;  // MAS §3.5
    localparam ADDR_INT_STATUS     = 12'h058;  // relocated by design review
    localparam ADDR_DBG_CTRL       = 12'h060;  // MAS §3.6
    localparam ADDR_DBG_STATE      = 12'h064;
    localparam ADDR_DBG_OBS_SEL    = 12'h068;
    localparam ADDR_DBG_TRACE      = 12'h06C;
    localparam ADDR_DBG_SCRATCH    = 12'h070;  // UNDOCUMENTED: temporary hook

    // ---- CSR storage ----
    logic [31:0] ctrl_reg, cfg_reg, status_reg;
    logic [31:0] ring_base_reg, ring_head_reg, ring_tail_reg, ring_size_reg;
    logic [31:0] perf_bytes_in_reg, perf_bytes_out_reg, perf_jobs_reg;
    logic [31:0] perf_cycles_reg, perf_hits_reg, arb_grants_reg;
    logic [31:0] error_reg, err_addr_reg, err_info_reg;
    logic [31:0] int_en_reg, int_status_reg;
    logic [31:0] dbg_ctrl_reg, dbg_state_reg, dbg_obs_sel_reg, dbg_trace_reg;
    logic [31:0] dbg_scratch_reg;

    // ---- Job-sequencer control FSM (MAS §4.1) ----
    // DRIFT: WRITE_OUT state is missing; output drain is folded into DONE.
    typedef enum logic [2:0] {
        IDLE,
        FETCH_JOB,
        LOAD_DATA,
        COMPRESS,
        DONE
    } control_fsm_e;

    control_fsm_e control_fsm;

    always_ff @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            control_fsm       <= IDLE;
            ctrl_reg          <= 32'h0;
            status_reg        <= 32'h1;      // IDLE
            error_reg         <= 32'h0;
            int_status_reg    <= 32'h0;
            perf_jobs_reg     <= 32'h0;
        end else begin
            case (control_fsm)
                IDLE:      if (ctrl_reg[0]) control_fsm <= FETCH_JOB;
                FETCH_JOB: control_fsm <= LOAD_DATA;
                LOAD_DATA: control_fsm <= COMPRESS;
                COMPRESS:  control_fsm <= DONE;
                DONE: begin
                    perf_jobs_reg <= perf_jobs_reg + 1'b1;
                    control_fsm   <= IDLE;
                end
                default:   control_fsm <= IDLE;
            endcase
        end
    end

    assign s_axi_awready = 1'b1;
    assign s_axi_wready  = 1'b1;
    assign s_axi_arready = 1'b1;
    assign s_axi_rvalid  = 1'b1;
    assign s_axi_rdata   = status_reg;
    assign m_axi_wdata   = 32'h0;
    assign m_axi_wvalid  = 1'b0;
    assign irq           = int_status_reg[0] & int_en_reg[0];

endmodule
