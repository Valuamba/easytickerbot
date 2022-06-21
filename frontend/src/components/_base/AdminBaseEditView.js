import React, { useState } from "react";

import { NavLink as RouterLink, useHistory } from "react-router-dom";

import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography";
import Grid from "@material-ui/core/Grid";
import makeStyles from "@material-ui/core/styles/makeStyles";

import SaveIcon from "@material-ui/icons/Save";
import DeleteIcon from "@material-ui/icons/Delete";

import { getItemValue, renderEditField } from "./edit";
import { callApi } from "../../lib/api";
import Alert from "@material-ui/lab/Alert";
import CircularProgress from "@material-ui/core/CircularProgress";

const useStyles = makeStyles((theme) => ({
  title: {
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(2),
  },
  alert: {
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(1),
  },
  formField: {
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(3),
  },
  form: {
    maxWidth: 700,
  },
  formControls: {
    marginTop: theme.spacing(2),
  },
  formControlsColumn: {
    marginBottom: theme.spacing(2),
  },
  deleteButton: {
    marginLeft: theme.spacing(2),
  },
  extraEditFields: {
    marginTop: 10,
    marginBottom: 10,
  },
}));

export default function AdminBaseEditView(props) {
  const { meta, isLoaded, item, breadcrumbs } = props;

  const classes = useStyles();
  const history = useHistory();

  const [formValues, setFormValues] = useState(null);
  const [formErrors, setFormErrors] = useState({});
  const [isSaving, setIsSaving] = useState(false);

  function setNonFieldFormError(errorText) {
    setFormErrors({
      non_field_errors: [errorText],
    });
  }

  if (!isLoaded) {
    return <div></div>;
  }

  const filteredEditFields = meta.getEditFields();

  if (formValues === null) {
    const initialFormValues = {};
    filteredEditFields.forEach((field, i) => {
      initialFormValues[field.key] = getItemValue(item, field.key);
    });
    setFormValues(initialFormValues);
    return <div></div>;
  }

  function formSubmitHandler(event) {
    event.preventDefault();

    const targetUrl = item
      ? meta.getEntityApiUrl(item.id)
      : meta.entityListApiUrl;

    const targetMethod = item ? "PUT" : "POST";

    setIsSaving(true);

    callApi(targetUrl, targetMethod, meta.createSaveData(formValues)).then(
      ({ data, response }) => {
        setIsSaving(false);
        setFormErrors({});
        switch (response.status) {
          case 400:
            return setFormErrors(data);
          case 403:
            if (data.detail) {
              return setNonFieldFormError(data.detail);
            }
          default:
            history.push(meta.getShowPath(data.id));
        }
      }
    );
  }

  return (
    <div>
      {/* Breadcrumbs */}
      {breadcrumbs}

      {/* Title */}
      <Typography className={classes.title} component="h1" variant="h5">
        {item
          ? `Редактирование ${meta.nameCases.second}`
          : `Добавить ${meta.nameCases.fourth}`}
      </Typography>

      {formErrors.non_field_errors && (
        <Alert className={classes.alert} severity="error">
          {formErrors.non_field_errors.join(" ")}
        </Alert>
      )}

      {/* Entity data */}
      <form className={classes.form} onSubmit={formSubmitHandler}>
        <div>
          {filteredEditFields.map((field, i) => (
            <div key={i} className={classes.formField}>
              {renderEditField(
                field,
                formValues,
                setFormValues,
                formErrors,
                item
              )}
            </div>
          ))}
        </div>
        {meta.blocks.extraEditFields && (
          <div className={classes.extraEditFields}>
            {meta.blocks.extraEditFields(item)}
          </div>
        )}
        <Grid className={classes.formControls} container>
          <Grid className={classes.formControlsColumn} item xs>
            <Button
              variant="contained"
              color="primary"
              startIcon={<SaveIcon />}
              type="submit"
            >
              Сохранить
            </Button>
            {isSaving && (
              <CircularProgress
                style={{ marginLeft: 15, top: 8, position: "relative" }}
                size={23}
              />
            )}
          </Grid>
          <Grid className={classes.formControlsColumn}>
            {item && (
              <Button
                className={classes.deleteButton}
                component={RouterLink}
                to={meta.getDeletePath(item.id)}
                variant="outlined"
                color="secondary"
                startIcon={<DeleteIcon />}
              >
                Удалить
              </Button>
            )}
          </Grid>
        </Grid>
      </form>
    </div>
  );
}
