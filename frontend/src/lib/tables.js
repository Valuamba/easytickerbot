import TableRow from "@material-ui/core/TableRow";
import TableCell from "@material-ui/core/TableCell";
import React from "react";

export function SimpleTableRow(props) {
  return (
    <TableRow>
      <TableCell component="th" scope="row">
        {props.label}
      </TableCell>
      <TableCell>{props.value}</TableCell>
    </TableRow>
  );
}
