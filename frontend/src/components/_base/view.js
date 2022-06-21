import moment from "moment";

import React from "react";

import Link from "@material-ui/core/Link";

export function renderValue(item, field) {
  return formatValue(getValue(item, field.key), field.type);
}

export function getValue(item, key) {
  if (typeof key === "function") {
    return key(item);
  } else {
    return item[key];
  }
}

export function formatValue(value, fieldType) {
  switch (fieldType) {
    case "datetime":
      // NOTE: can be optimized
      if (!value) {
        return "-";
      }
      return moment(value).format("DD.MM.YYYY H:mm:ss");
    case "qr_image":
      return <img src={value} />;
    case "link":
      return (
        <Link href={value} target="_blank">
          {value}
        </Link>
      );
    default:
      return value;
  }
}
