import React from "react";

import AdminView from "../_base/AdminView";
import AdminViewMeta from "../_base/AdminViewMeta";

const LIST_FIELDS = [
  {
    name: "Telegram ID",
    key: "telegram_id",
  },
  {
    name: "Имя",
    key: "first_name",
  },
  {
    name: "Фамилия",
    key: "last_name",
  },
  {
    name: "Имя пользователя",
    key: "username",
  },
  {
    name: "Заблокирован",
    key: (i) => (i.is_blocked ? "Да" : "Нет"),
    realKey: "is_blocked",
  },
];

export default function ParticipantsView({ accountRole }) {
  const meta = new AdminViewMeta({
    basePath: "/participants",
    nameCases: {
      first: "участник",
      firstMultiple: "участники",
      second: "участника",
      fourth: "участника",
    },
    entityListApiUrl: "/management-api/participants/",
    entityApiUrlPattern: "/management-api/participants/:id/",
    showFields: LIST_FIELDS.concat([
      {
        name: "Дата создания",
        key: "created_at",
        type: "datetime",
      },
    ]),
    editFields: [
      {
        name: "Telegram ID",
        key: "telegram_id",
        isRequired: true,
      },
      {
        name: "Имя",
        key: "first_name",
      },
      {
        name: "Фамилия",
        key: "last_name",
      },
      {
        name: "Имя пользователя",
        key: "username",
      },
      {
        name: "Заблокирован",
        key: "is_blocked",
        type: "checkbox",
      },
    ],
    listFields: LIST_FIELDS,
    linkedListFields: ["telegram_id"],
    accountRole,
  });

  return <AdminView meta={meta} />;
}
