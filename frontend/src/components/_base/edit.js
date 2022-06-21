import moment from "moment";

import React, { useEffect, useState } from "react";

import IconButton from "@material-ui/core/IconButton";
import TextField from "@material-ui/core/TextField";
import FormControl from "@material-ui/core/FormControl";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import FormHelperText from "@material-ui/core/FormHelperText";
import Checkbox from "@material-ui/core/Checkbox";
import Divider from "@material-ui/core/Divider";
import Autocomplete from "@material-ui/lab/Autocomplete";
import { DateTimePicker, MuiPickersUtilsProvider } from "@material-ui/pickers";
import MomentUtils from "@date-io/moment";
import "moment/locale/ru";
import PhotoCameraIcon from "@material-ui/icons/PhotoCamera";

import { callApi } from "../../lib/api";
import { Link } from "@material-ui/core";

const NO_OPTIONS_TEXT = "Нет доступных вариантов";

function ImageUpload(props) {
  const { field, value, label, onNewValue, error, helperText, item } = props;

  const [apiError, setApiError] = useState(null);

  function handleFileInputChange(event) {
    setApiError(null);
    if (event.target.files.length === 0) {
      return;
    }
    const file = event.target.files[0];
    // TODO: add content type: multipart form data
    callApi(
      "/fileuploads/upload/image",
      "POST",
      file,
      { "Content-Disposition": `attachment; filename="${file.name}"` },
      false
    )
      .then(function ({ data, response }) {
        const apiErrorMessage = response.headers.get("x-api-error");
        if (apiErrorMessage === "too_large") {
          setApiError("Максимальный размер файла 50 МБ.");
          return;
        }
        const uploadId = response.headers.get("x-upload-id");
        onNewValue(uploadId);
      })
      .catch(function () {
        console.log("Error", arguments);
      });
  }

  function handleDelete(event) {
    event.preventDefault();
    onNewValue(null);
  }

  const [thumbnailUrl, setThumbnailUrl] = useState(null);
  const [fileUrl, setFileUrl] = useState(null);
  const [isVideo, setIsVideo] = useState(false);

  useEffect(() => {
    if (!value) {
      setThumbnailUrl(null);
      setFileUrl(null);
      return;
    }
    callApi(`/management-api/image-uploads/${value}/`).then(({ data }) => {
      setThumbnailUrl(data.thumbnail_url);
      setFileUrl(data.file);
      setIsVideo(data.is_video);
    });
  }, [value]);

  return (
    <div>
      <input
        accept="image/*,.mp4"
        style={{ display: "none" }}
        id="icon-button-file"
        type="file"
        onChange={handleFileInputChange}
      />
      <label htmlFor="icon-button-file">
        {label}
        <IconButton color="primary" component="span">
          <PhotoCameraIcon />
        </IconButton>
      </label>
      <div>
        {thumbnailUrl && fileUrl && (
          <div>
            <a href={fileUrl} target="_blank">
              {isVideo ? (
                <video
                  style={{ maxWitdh: "100%", maxHeight: 350 }}
                  src={thumbnailUrl}
                ></video>
              ) : (
                <img style={{ maxWitdh: "100%" }} src={thumbnailUrl} />
              )}
            </a>
            <br />
            <Link onClick={handleDelete} href="#delete-poster">
              Удалить
            </Link>
          </div>
        )}
      </div>
      {apiError && <div style={{ color: "red" }}>{apiError}</div>}
    </div>
  );
}

function FetchAutocomplete(props) {
  const { field, value, label, onChange, error, helperText, item } = props;
  const [values, setValues] = useState([]);

  function fetchValues(searchText) {
    const fetchUrl = `${field.fetchUrl}${
      searchText ? "?search=" + encodeURIComponent(searchText) : ""
    }`;

    callApi(fetchUrl).then(({ data }) => {
      const results = data ? data["results"] || [] : [];
      setValues(
        field.filterValues ? field.filterValues(results, item) : results
      );
    });
  }

  function handleInputChange(event, inputText, reason) {
    fetchValues(inputText);
  }

  useEffect(() => {
    fetchValues();
  }, []);

  return (
    <Autocomplete
      id={field.key}
      multiple={field.isMultiple || undefined}
      filterSelectedOptions={field.isMultiple || undefined}
      getOptionLabel={field.toLabel}
      getOptionSelected={(option, value) => option.id === value.id}
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
          error={error}
          helperText={helperText}
        />
      )}
      options={values}
      value={field.isMultiple ? value || [] : value}
      onChange={onChange}
      noOptionsText={NO_OPTIONS_TEXT}
      onInputChange={handleInputChange}
    />
  );
}

export function getItemValue(item, key) {
  return item ? item[key] : undefined;
}

export function renderEditField(
  field,
  formValues,
  setFormValues,
  formErrors,
  item
) {
  const label = `${field.name}${field.isRequired ? " *" : ""}`;
  const errorList = formErrors ? formErrors[field.realKey || field.key] : null;
  const errorText = errorList ? errorList.join(" ") : "";

  function handleNewValue(newValue) {
    setFormValues(Object.assign({}, formValues, { [field.key]: newValue }));
  }

  const value = formValues[field.key];

  switch (field.type) {
    case "checkbox":
      return (
        <FormControl error={!!errorText}>
          <FormControlLabel
            control={<Checkbox checked={value || false} name={field.key} />}
            label={label}
            onChange={(e, newValue) => handleNewValue(newValue)}
          />
          <FormHelperText>{errorText}</FormHelperText>
        </FormControl>
      );
    case "autocomplete":
      return (
        <FetchAutocomplete
          field={field}
          value={value || null}
          label={label}
          onChange={(e, newValue) => handleNewValue(newValue)}
          error={!!errorText}
          helperText={errorText}
          noOptionsText={NO_OPTIONS_TEXT}
          item={item}
        />
      );
    case "select":
      return (
        <Autocomplete
          id={field.key}
          getOptionLabel={(option) => field.choices[option]}
          renderInput={(params) => (
            <TextField
              {...params}
              label={label}
              error={!!errorText}
              helperText={errorText}
            />
          )}
          options={Object.keys(field.choices)}
          onChange={(e, newValue) => handleNewValue(newValue)}
          value={value || null}
        />
      );
    case "datetime":
      return (
        <MuiPickersUtilsProvider
          libInstance={moment}
          utils={MomentUtils}
          locale="ru"
        >
          <DateTimePicker
            id={field.key}
            value={value || null}
            disablePast
            fullWidth
            clearable
            onChange={(v) => handleNewValue(v)}
            label={label}
            showTodayButton
            error={!!errorText}
            helperText={errorText}
          />
        </MuiPickersUtilsProvider>
      );
    case "password":
      return (
        <TextField
          id={field.key}
          label={label}
          fullWidth
          type="password"
          onChange={(e) => handleNewValue(e.target.value)}
          error={!!errorText}
          helperText={errorText}
        />
      );
    case "imageReadonly":
      return (
        <div>
          <img style={{ maxWidth: "100%" }} src={value} />
        </div>
      );
    case "imageupload":
      return (
        <ImageUpload
          field={field}
          value={value}
          label={label}
          onNewValue={(newValue) => handleNewValue(newValue)}
        />
      );
    case "readonly":
      return (
        <TextField
          id={field.key}
          label={label}
          value={value || ""}
          fullWidth
          error={!!errorText}
          helperText={errorText}
          disabled
        />
      );
    case "divider":
      return (
        <div>
          <Divider />
        </div>
      );
    default:
      return (
        <TextField
          id={field.key}
          label={label}
          value={value || ""}
          onChange={(e) => handleNewValue(e.target.value)}
          fullWidth
          multiline={field.multiline}
          rows={field.multiline ? 4 : undefined}
          type={field.type === "number" ? "number" : "text"}
          error={!!errorText}
          helperText={errorText || field.hint}
        />
      );
  }
}
