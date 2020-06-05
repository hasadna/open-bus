import React from "react";
import { KeyboardDatePicker, MuiPickersUtilsProvider } from "@material-ui/pickers";
import DateFnsUtils from "@date-io/date-fns";

function DateSelector(props) {
    return (
      <MuiPickersUtilsProvider utils={DateFnsUtils}>
        <KeyboardDatePicker
          value={props.value}
          onChange={props.onChange}
          variant="inline"
          disableToolbar
          format="dd/MM/yyyy"
          autoOk={true}
          disableFuture={true}
          margin="normal"
          label="Date:"
          emptyLabel="Select..."
          KeyboardButtonProps={{
            "aria-label": "change date",
          }}
        />
      </MuiPickersUtilsProvider>
    );
  }

  export default DateSelector;