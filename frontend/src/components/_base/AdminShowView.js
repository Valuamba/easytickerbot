import { capitalize } from "lodash/string";

import React, { useEffect, useState } from "react";

import { useParams, NavLink as RouterLink } from "react-router-dom";

import Typography from "@material-ui/core/Typography";
import Button from "@material-ui/core/Button";
import makeStyles from "@material-ui/core/styles/makeStyles";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableRow from "@material-ui/core/TableRow";
import TableCell from "@material-ui/core/TableCell";

import EditIcon from "@material-ui/icons/Edit";

import { callApi } from "../../lib/api";

import { renderValue } from "./view";
import Grid from "@material-ui/core/Grid";
import SaveIcon from "@material-ui/icons/Save";
import DeleteIcon from "@material-ui/icons/Delete";

const useStyles = makeStyles((theme) => ({
  title: {
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(2),
  },
  formControls: {
    marginTop: theme.spacing(2),
  },
  formControlsColumn: {
    marginBottom: theme.spacing(2),
  },
  labelCell: {
    width: 180,
  },
}));

export default function AdminShowView(props) {
  const { meta } = props;
  const { entityId } = useParams();

  const [isLoaded, setIsLoaded] = useState(false);
  const [item, setItem] = useState(null);
  const classes = useStyles();

  useEffect(() => {
    callApi(meta.getEntityApiUrl(entityId)).then(({ data }) => {
      setItem(data);
      setIsLoaded(true);
    });
  }, []);

  if (!isLoaded) {
    return <div></div>;
  }

  return (
    <div>
      {/* Breadcrumbs */}
      {meta.getShowBreadcrumbs(entityId)}

      {/* Title */}
      <Typography className={classes.title} component="h1" variant="h5">
        {capitalize(meta.nameCases.first)}
      </Typography>

      {/* Entity data */}
      <Table>
        <TableBody>
          {meta.showFields.map((field, i) => (
            <TableRow key={i}>
              <TableCell className={classes.labelCell} align="right">
                <b>{field.name}:</b>
              </TableCell>
              <TableCell>{renderValue(item, field)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <Grid className={classes.formControls} container>
        <Grid className={classes.formControlsColumn} item xs>
          {!meta.editingDisabled && (
            <Button
              component={RouterLink}
              to={meta.getEditPath(entityId)}
              variant="contained"
              color="primary"
              startIcon={<EditIcon />}
            >
              Редактировать
            </Button>
          )}
        </Grid>
        <Grid className={classes.formControlsColumn}>
          {meta.blocks.extraShowControls &&
            meta.blocks.extraShowControls(entityId)}
        </Grid>
      </Grid>
    </div>
  );
}
