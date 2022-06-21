import React, { useEffect, useState } from "react";

import { useParams } from "react-router-dom";

import { callApi } from "../../lib/api";

import AdminBaseEditView from "./AdminBaseEditView";

export default function AdminEditView(props) {
  const { meta } = props;
  const { entityId } = useParams();

  const [isLoaded, setIsLoaded] = useState(false);
  const [item, setItem] = useState(null);

  useEffect(() => {
    callApi(meta.getEntityApiUrl(entityId)).then(({ data }) => {
      setItem(data);
      setIsLoaded(true);
    });
  }, []);

  return (
    <AdminBaseEditView
      meta={meta}
      isLoaded={isLoaded}
      item={item}
      breadcrumbs={meta.getEditBreadcrumbs(entityId)}
    />
  );
}
