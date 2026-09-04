// -----------------------------------------------------------------------------
// zephyr_coss_ctrl_fsm.sv — job-sequencer FSM for the Zephyr COSS (MAS §4.1).
//
// Deliberate demo drift: the MAS requires the states
//   IDLE, FETCH_JOB, LOAD_DATA, COMPRESS, WRITE_OUT, DONE
// but this implementation folds the output-drain (WRITE_OUT) into DONE, so the
// WRITE_OUT state is MISSING (caught at milestone 0.5).
// -----------------------------------------------------------------------------
module zephyr_coss_ctrl_fsm (
    input  wire        aclk,
    input  wire        aresetn,
    input  wire        job_start,
    input  wire        accel_busy,
    output reg         job_done,
    output reg         job_error,
    output reg  [31:0] status
);

    // NOTE: WRITE_OUT state intentionally omitted (MAS §4.1 drift).
    typedef enum logic [2:0] {
        IDLE,
        FETCH_JOB,
        LOAD_DATA,
        COMPRESS,
        DONE
    } control_fsm_e;

    control_fsm_e control_fsm, next_state;

    always_ff @(posedge aclk or negedge aresetn) begin
        if (!aresetn) control_fsm <= IDLE;
        else          control_fsm <= next_state;
    end

    always_comb begin
        next_state = control_fsm;
        unique case (control_fsm)
            IDLE:      if (job_start)  next_state = FETCH_JOB;
            FETCH_JOB:                 next_state = LOAD_DATA;
            LOAD_DATA:                 next_state = COMPRESS;
            COMPRESS:  if (!accel_busy) next_state = DONE;
            DONE:                      next_state = IDLE;
            default:                   next_state = IDLE;
        endcase
    end

    always_ff @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            job_done  <= 1'b0;
            job_error <= 1'b0;
            status    <= 32'h1;
        end else begin
            job_done <= (control_fsm == DONE);
            status   <= {29'h0, control_fsm};
        end
    end

endmodule
