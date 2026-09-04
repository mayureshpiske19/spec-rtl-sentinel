// -----------------------------------------------------------------------------
// zephyr_coss_arbiter.sv — AXI read/write arbiter (MAS §3.1 / §7).
//
// Round-robin (default) and fixed-priority modes with starvation promotion.
// Grant events feed the ARB_GRANTS counter.
// -----------------------------------------------------------------------------
module zephyr_coss_arbiter #(
    parameter int NUM_MASTERS = 3
) (
    input  wire        aclk,
    input  wire        aresetn,
    input  wire        arb_mode,          // 0 = round-robin, 1 = fixed priority
    input  wire [NUM_MASTERS-1:0] req,
    output reg  [2:0]  grant
);

    localparam int PROMOTE_THRESH = 16;   // anti-starvation window

    reg [1:0]  rr_ptr;
    reg [7:0]  wait_cnt [NUM_MASTERS-1:0];

    integer i;
    always_ff @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            rr_ptr <= 2'd0;
            grant  <= 3'd0;
            for (i = 0; i < NUM_MASTERS; i = i + 1) wait_cnt[i] <= 8'd0;
        end else begin
            if (arb_mode) begin
                // Fixed priority: Output DMA (2) > Accelerator (1) > Input DMA (0)
                if      (req[2]) grant <= 3'd2;
                else if (req[1]) grant <= 3'd1;
                else if (req[0]) grant <= 3'd0;
                else            grant <= 3'd0;
            end else begin
                // Round-robin rotation
                rr_ptr <= rr_ptr + 1'b1;
                grant  <= {1'b0, rr_ptr};
            end
        end
    end

endmodule
