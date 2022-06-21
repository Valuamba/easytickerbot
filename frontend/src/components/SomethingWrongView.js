import React from "react";

import Typography from "@material-ui/core/Typography";
import Avatar from "@material-ui/core/Avatar";
import Button from "@material-ui/core/Button";
import Container from "@material-ui/core/Container";
import ErrorOutlined from "@material-ui/icons/ErrorOutlined";
import Refresh from "@material-ui/icons/Refresh";
import makeStyles from "@material-ui/core/styles/makeStyles";

const useStyles = makeStyles((theme) => ({
  paper: {
    marginTop: theme.spacing(8),
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  subtitle: {
    marginTop: theme.spacing(2),
  },
  controls: {
    marginTop: theme.spacing(2),
  },
}));

export default function SomethingWrongView() {
  const classes = useStyles();

  return (
    <Container component="main" maxWidth="xs">
      <div className={classes.paper}>
        <Avatar>
          <ErrorOutlined />
        </Avatar>
        <Typography className={classes.subtitle} component="h6" variant="h6">
          Что-то пошло не так...
        </Typography>
        <div className={classes.controls}>
          <Button
            onClick={function () {
              window.location.reload();
            }}
            color="primary"
            variant="contained"
            startIcon={<Refresh />}
          >
            Перезагрузить страницу
          </Button>
        </div>
      </div>
    </Container>
  );
}
