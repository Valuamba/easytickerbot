import React from "react";

import CssBaseline from "@material-ui/core/CssBaseline";

import SignInView from "./sign-in/SignInView";
import SomethingWrongView from "./SomethingWrongView";
import MainView from "./MainView";

export class App extends React.Component {
  constructor() {
    super();

    this.state = {
      isLoaded: false,
      somethingWrong: false,
      isAuthenticated: false,
      accountEmail: undefined,
    };
  }

  componentDidMount() {
    const token = localStorage.getItem("auth_token");
    const drawerIsOpenSaved = localStorage.getItem("drawer_is_open") === "true";

    if (token) {
      fetch("/management-api/account", {
        headers: { Authorization: `Token ${token}` },
      })
        .then((response) => {
          if (response.ok) {
            return response.json();
          } else {
            this.setState({ isLoaded: true });
          }
        })
        .then((data) => {
          if (data && data.email) {
            this.setState({
              isAuthenticated: true,
              isLoaded: true,
              accountEmail: data.email,
              accountRole: data.role,
              drawerIsOpenSaved: drawerIsOpenSaved,
            });
          }
        })
        .catch(() => {
          this.setState({ somethingWrong: true });
        });
    } else {
      this.setState({ isLoaded: true });
    }
  }

  render() {
    return (
      <React.Fragment>
        <CssBaseline />
        {this.state.somethingWrong ? (
          <SomethingWrongView />
        ) : (
          this.state.isLoaded &&
          (this.state.isAuthenticated ? (
            <MainView
              accountEmail={this.state.accountEmail}
              accountRole={this.state.accountRole}
              drawerIsOpenSaved={this.state.drawerIsOpenSaved}
            />
          ) : (
            <SignInView />
          ))
        )}
      </React.Fragment>
    );
  }
}
