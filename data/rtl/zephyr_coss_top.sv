// -----------------------------------------------------------------------------
// zephyr_coss_top.sv  (SYNTHETIC RTL for the Spec-RTL Sentinel demo)
//
// Top level of the Zephyr LZ Compression Offload Sub-System (COSS). Wires the
// control plane (CSR + job-sequencer FSM) to the datapath (AXI arbiter, L2
// cache, and the LZ accelerator). See data/doc/zephyr_coss_mas.md.
//
// NOTE (deliberate demo drift): the accelerator memory write-data bus
// `m_axi_wdata` is declared 32-bit here; MAS §2.1 requires 64-bit  -> WIDTH DRIFT
// -----------------------------------------------------------------------------
module zephyr_coss_top #(
    parameter int ADDR_WIDTH = 12,
    parameter int DATA_WIDTH = 64,     // intended memory data width (MAS §2.1)
    parameter int NUM_MASTERS = 3
) (
    input  wire        aclk,
    input  wire        aresetn,        // active-low async-assert/sync-release

    // ---- AXI4-Lite CSR subordinate (firmware register access) ----
    input  wire [11:0] s_axi_awaddr,   // 12-bit CSR address (MAS §2.3)
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
    output wire [31:0] m_axi_wdata,    // DRIFT: MAS §2.1 requires 64-bit
    output wire        m_axi_wvalid,
    input  wire        m_axi_wready,

    // ---- System ----
    output wire        irq,
    input  wire        scan_en          // scan-based DFT enable (MAS §5.1)
);

    // ---- Control/datapath interconnect signals ----
    logic        job_start, job_done, job_error;
    logic [2:0]  arb_grant;
    logic        cache_hit, cache_miss;
    logic [31:0] accel_comp_size;
    logic        accel_busy;
    logic [31:0] ctrl_to_csr_status;

    // ---- CSR register file + job control ----
    zephyr_coss_csr u_csr (
        .aclk           (aclk),
        .aresetn        (aresetn),
        .s_axi_awaddr   (s_axi_awaddr),
        .s_axi_awvalid  (s_axi_awvalid),
        .s_axi_awready  (s_axi_awready),
        .s_axi_wdata    (s_axi_wdata),
        .s_axi_wvalid   (s_axi_wvalid),
        .s_axi_wready   (s_axi_wready),
        .s_axi_araddr   (s_axi_araddr),
        .s_axi_arvalid  (s_axi_arvalid),
        .s_axi_arready  (s_axi_arready),
        .s_axi_rdata    (s_axi_rdata),
        .s_axi_rvalid   (s_axi_rvalid),
        .job_start      (job_start),
        .job_done       (job_done),
        .job_error      (job_error),
        .cache_hit      (cache_hit),
        .cache_miss     (cache_miss),
        .arb_grant      (arb_grant),
        .irq            (irq),
        .scan_en        (scan_en)
    );

    // ---- Job-sequencer FSM ----
    zephyr_coss_ctrl_fsm u_ctrl (
        .aclk           (aclk),
        .aresetn        (aresetn),
        .job_start      (job_start),
        .accel_busy     (accel_busy),
        .job_done       (job_done),
        .job_error      (job_error),
        .status         (ctrl_to_csr_status)
    );

    // ---- AXI arbiter ----
    zephyr_coss_arbiter #(.NUM_MASTERS(NUM_MASTERS)) u_arb (
        .aclk           (aclk),
        .aresetn        (aresetn),
        .grant          (arb_grant)
    );

    // ---- L2 cache ----
    zephyr_coss_cache u_cache (
        .aclk           (aclk),
        .aresetn        (aresetn),
        .hit            (cache_hit),
        .miss           (cache_miss)
    );

    // ---- LZ accelerator ----
    zephyr_coss_lz_accel u_accel (
        .aclk           (aclk),
        .aresetn        (aresetn),
        .start          (job_start),
        .busy           (accel_busy),
        .comp_size      (accel_comp_size),
        .m_axi_wdata    (m_axi_wdata),
        .m_axi_wvalid   (m_axi_wvalid),
        .m_axi_wready   (m_axi_wready)
    );

endmodule
