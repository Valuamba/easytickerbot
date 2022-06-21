import React from "react";
import { Route, Switch, useRouteMatch } from "react-router-dom";
import AdminListView from "./AdminListView";
import AdminAddView from "./AdminAddView";
import AdminDeleteView from "./AdminDeleteView";
import AdminEditView from "./AdminEditView";
import AdminShowView from "./AdminShowView";

export default function AdminView(props) {
  const match = useRouteMatch();

  const { meta } = props;

  return (
    <div>
      <Switch>
        <Route path={`${match.path}/add`}>
          <AdminAddView meta={meta} />
        </Route>
        <Route path={`${match.path}/:entityId/delete`}>
          <AdminDeleteView meta={meta} />
        </Route>
        <Route path={`${match.path}/:entityId/edit`}>
          <AdminEditView meta={meta} />
        </Route>
        <Route path={`${match.path}/:entityId`}>
          <AdminShowView meta={meta} />
        </Route>
        <Route path={match.path}>
          <AdminListView meta={meta} />
        </Route>
      </Switch>
    </div>
  );
}
