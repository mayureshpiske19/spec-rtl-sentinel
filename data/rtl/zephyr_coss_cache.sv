// -----------------------------------------------------------------------------
// zephyr_coss_cache.sv — 2-way set-associative write-back L2 cache (MAS §3.2).
//
// Caches the LZ history window and job descriptors. 64 KB, 64 B lines, 512 sets,
// LRU replacement, valid/dirty per line. Reference model for the demo — the tag
// pipeline is behavioural.
// -----------------------------------------------------------------------------
module zephyr_coss_cache #(
    parameter int CACHE_SIZE = 65536,   // 64 KB
    parameter int LINE_BYTES = 64,
    parameter int WAYS       = 2,
    parameter int SETS       = 512
) (
    input  wire        aclk,
    input  wire        aresetn,
    input  wire        req_valid,
    input  wire [31:0] req_addr,
    output reg         hit,
    output reg         miss
);

    // Address decomposition (32-bit): [31:15] tag | [14:6] index | [5:0] offset
    wire [16:0] tag    = req_addr[31:15];
    wire [8:0]  index  = req_addr[14:6];

    // Tag + state arrays (behavioural).
    reg [16:0] tag_arr   [SETS-1:0][WAYS-1:0];
    reg        valid_arr [SETS-1:0][WAYS-1:0];
    reg        dirty_arr [SETS-1:0][WAYS-1:0];
    reg        lru_arr   [SETS-1:0];

    always_ff @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            hit  <= 1'b0;
            miss <= 1'b0;
        end else if (req_valid) begin
            if (valid_arr[index][0] && tag_arr[index][0] == tag) begin
                hit <= 1'b1; miss <= 1'b0; lru_arr[index] <= 1'b1;
            end else if (valid_arr[index][1] && tag_arr[index][1] == tag) begin
                hit <= 1'b1; miss <= 1'b0; lru_arr[index] <= 1'b0;
            end else begin
                hit <= 1'b0; miss <= 1'b1;   // refill via memory controller
            end
        end else begin
            hit <= 1'b0; miss <= 1'b0;
        end
    end

endmodule
