import React, { useState } from "react";

import Button from "@material-ui/core/Button";
import Container from "@material-ui/core/Container";
import TextField from "@material-ui/core/TextField";
import Typography from "@material-ui/core/Typography";
import makeStyles from "@material-ui/core/styles/makeStyles";
import Alert from "@material-ui/lab/Alert";

const useStyles = makeStyles((theme) => ({
  paper: {
    marginTop: theme.spacing(8),
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  submit: {
    marginTop: theme.spacing(1),
  },
  alert: {
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(1),
  },
}));

export default function SignInView() {
  const classes = useStyles();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [formError, setFormError] = useState();
  const [emailError, setEmailError] = useState();
  const [passwordError, setPasswordError] = useState();

  function handleEmailChange(event) {
    setEmail(event.target.value);
  }

  function handlePasswordChange(event) {
    setPassword(event.target.value);
  }

  function onFormSubmit(event) {
    event.preventDefault();

    fetch("/management-api/auth", {
      method: "POST",
      body: JSON.stringify({ username: email, password: password }),
      headers: {
        "Content-Type": "application/json",
      },
    }).then((response) => {
      response.json().then((data) => {
        setFormError(undefined);
        setEmailError(undefined);
        setPasswordError(undefined);

        if (response.status === 400) {
          data.non_field_errors &&
            setFormError(data.non_field_errors.join(" "));
          data.username && setEmailError(data.username.join(" "));
          data.password && setPasswordError(data.password.join(" "));
        } else {
          localStorage.setItem("auth_token", data.token);
          window.location.reload();
        }
      });
    });
  }

  return (
    <Container component="main" maxWidth="xs">
      <div className={classes.paper}>
        <Typography component="h1" variant="h5">
          Администрирование
        </Typography>
        {formError && (
          <Alert className={classes.alert} severity="error">
            {formError}
          </Alert>
        )}
        <form id="signin-form" onSubmit={onFormSubmit}>
          <TextField
            label="Email"
            fullWidth
            variant="outlined"
            required
            margin="normal"
            autoComplete="email"
            autoFocus
            name="email"
            onChange={handleEmailChange}
            value={email}
            error={emailError}
            helperText={emailError}
          />
          <TextField
            label="Пароль"
            fullWidth
            variant="outlined"
            required
            margin="normal"
            autoComplete="current-password"
            onChange={handlePasswordChange}
            type="password"
            error={passwordError}
            helperText={passwordError}
          />
          <div className={classes.submit}>
            <Button
              type="submit"
              color="primary"
              variant="contained"
              fullWidth
              size="large"
            >
              Войти
            </Button>
          </div>
        </form>
      </div>
    </Container>
  );
}
