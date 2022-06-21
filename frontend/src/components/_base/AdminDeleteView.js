import React, { useEffect, useState } from "react";

import { useHistory, useParams } from "react-router-dom";

import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography";
import makeStyles from "@material-ui/core/styles/makeStyles";

import { callApi } from "../../lib/api";

const useStyles = makeStyles((theme) => ({
  title: {
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(2),
  },
  confirmButton: {
    marginTop: theme.spacing(2),
  },
}));

export default function AdminDeleteView(props) {
  const { meta } = props;
  const { entityId } = useParams();

  const classes = useStyles();

  const [isLoaded, setIsLoaded] = useState(false);
  const [item, setItem] = useState(null);
  const history = useHistory();

  useEffect(() => {
    callApi(meta.getEntityApiUrl(entityId)).then(({ data }) => {
      setItem(data);
      setIsLoaded(true);
    });
  }, []);

  if (!isLoaded) {
    return <div></div>;
  }

  function deleteHandler(event) {
    callApi(meta.getEntityApiUrl(entityId), "DELETE").then(
      ({ data, response }) => {
        if (!response.ok) {
          alert("Произошла ошибка при удалении.");
          return;
        }
        history.push(meta.getListPath());
      }
    );
  }

  return (
    <div>
      {/* Breadcrumbs */}
      {meta.getDeleteBreadcrumbs(entityId)}

      {/* Title */}
      <Typography className={classes.title} component="h1" variant="h5">
        Удаление {meta.nameCases.second}
      </Typography>

      {/* Entity data */}
      <div>
        Вы подтверждаете удаление {meta.nameCases.second} #{entityId}?
      </div>
      <Button
        className={classes.confirmButton}
        variant="contained"
        color="secondary"
        onClick={deleteHandler}
      >
        Удалить
      </Button>
    </div>
  );
}
