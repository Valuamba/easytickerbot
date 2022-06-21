export function callApi(
  path,
  method = "GET",
  data = null,
  extraHeaders = {},
  useJson = true
) {
  const authToken = localStorage.getItem("auth_token");

  const contentTypeHeader = {};

  if (useJson) {
    var body = data ? JSON.stringify(data) : null;
    contentTypeHeader["Content-Type"] = "application/json";
  } else {
    var body = data;
  }

  return fetch(
    path,
    Object.assign(
      {},
      {
        method: method || "GET",
        headers: {
          Authorization: `Token ${authToken}`,
          ...contentTypeHeader,
          ...extraHeaders,
        },
      },
      body === null ? {} : { body }
    )
  ).then((response) => {
    if (response.status === 204) {
      return { data: {}, response: response };
    }
    return response.json().then((data) => {
      return { data: data, response: response };
    });
  });
}
