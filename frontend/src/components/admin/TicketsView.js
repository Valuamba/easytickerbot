import React from "react";

import AdminView from "../_base/AdminView";
import AdminViewMeta from "../_base/AdminViewMeta";
import { renderSublocationName } from "../../lib/render";

const LIST_FIELDS = [
  {
    name: "ID",
    key: "id",
  },
  {
    name: "Событие",
    key: (i) =>
      i.category_data
        ? i.category_data.event_data
          ? i.category_data.event_data.name
          : "-"
        : "-",
    realKey: "category__event",
  },
  {
    name: "Стоимость при покупке",
    key: "purchase_price",
  },
  {
    name: "ID оплаты",
    key: "payment_id",
  },
  {
    name: "Гостевой инвайт",
    key: (i) => (i.guest_invite_data ? `#${i.guest_invite_data.id}` : "-"),
  },
  {
    name: "Участник",
    key: (i) => (i.participant_data ? i.participant_data.label : "-"),
    realKey: "participant",
  },
  {
    name: "Статус",
    key: (i) => i.status_label,
    realKey: "status",
  },
  {
    name: "Комментарий от пропускного контроля",
    key: "access_control_comment",
    disableOrdering: true,
  },
  {
    name: "Дата создания",
    key: "created_at",
    type: "datetime",
  },
];

export default function TicketsView({ accountRole }) {
  const meta = new AdminViewMeta({
    basePath: "/tickets",
    nameCases: {
      first: "билет",
      firstMultiple: "билеты",
      second: "билета",
      fourth: "билет",
    },
    entityListApiUrl: "/management-api/tickets/",
    entityApiUrlPattern: "/management-api/tickets/:id/",
    showFields: LIST_FIELDS.concat([]),
    editFields: [],
    listFields: LIST_FIELDS,
    linkedListFields: ["id"],
    accountRole,
    editingDisabled: true,
  });

  return <AdminView meta={meta} />;
}
