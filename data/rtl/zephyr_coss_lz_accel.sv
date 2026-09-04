// -----------------------------------------------------------------------------
// zephyr_coss_lz_accel.sv — LZ77 compression accelerator (MAS §3.4).
//
// Pipeline: Input FIFO -> Match Finder -> History Window -> Token Encoder ->
// (optional Huffman) -> CRC/Length -> Output FIFO. Behavioural reference model
// for the demo; emits compressed size and drives the output write channel.
//
// NOTE: the output write-data bus width is set at the top level; see
// zephyr_coss_top.sv (the 64-bit-vs-32-bit datapath drift lives there).
// -----------------------------------------------------------------------------
module zephyr_coss_lz_accel #(
    parameter int MIN_MATCH  = 3,
    parameter int MAX_MATCH  = 258,
    parameter int HASH_BITS  = 15,
    parameter int WINDOW_BYTES = 32768   // 32 KB history window
) (
    input  wire        aclk,
    input  wire        aresetn,
    input  wire        start,
    output reg         busy,
    output reg  [31:0] comp_size,

    output reg  [31:0] m_axi_wdata,
    output reg         m_axi_wvalid,
    input  wire        m_axi_wready
);

    // Local accelerator sub-FSM: LOAD -> MATCH -> EMIT -> FLUSH
    typedef enum logic [1:0] { A_LOAD, A_MATCH, A_EMIT, A_FLUSH } accel_state_e;
    accel_state_e accel_state;

    reg [31:0] byte_count;
    reg [14:0] hash_head [(1<<HASH_BITS)-1:0];

    always_ff @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            accel_state  <= A_LOAD;
            busy         <= 1'b0;
            comp_size    <= 32'h0;
            byte_count   <= 32'h0;
            m_axi_wvalid <= 1'b0;
            m_axi_wdata  <= 32'h0;
        end else begin
            unique case (accel_state)
                A_LOAD:  if (start) begin busy <= 1'b1; accel_state <= A_MATCH; end
                A_MATCH: accel_state <= A_EMIT;
                A_EMIT: begin
                    m_axi_wvalid <= 1'b1;
                    if (m_axi_wready) begin
                        comp_size   <= comp_size + 3'd4;
                        byte_count  <= byte_count + 3'd4;
                        accel_state <= A_FLUSH;
                    end
                end
                A_FLUSH: begin
                    m_axi_wvalid <= 1'b0;
                    busy         <= 1'b0;
                    accel_state  <= A_LOAD;
                end
                default: accel_state <= A_LOAD;
            endcase
        end
    end

endmodule
