import React from "react";
import AdminBaseEditView from "./AdminBaseEditView";

export default function AdminAddView(props) {
  const { meta } = props;

  return (
    <AdminBaseEditView
      meta={meta}
      isLoaded={true}
      breadcrumbs={meta.getAddBreadcrumbs()}
    />
  );
}
