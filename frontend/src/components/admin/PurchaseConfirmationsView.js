import React from "react";

import AdminView from "../_base/AdminView";
import AdminViewMeta from "../_base/AdminViewMeta";

const LIST_FIELDS = [
  {
    name: "ID",
    key: "id",
  },
  {
    name: "Участник",
    key: "participant_label",
    realKey: "ticket__participant",
  },
  {
    name: "Мероприятие",
    key: (i) => (i.event_data ? i.event_data.name : "-"),
    realKey: "ticket__category__event",
  },
  {
    name: "Категория билетов",
    key: (i) => (i.ticket_category_data ? i.ticket_category_data.name : "-"),
    realKey: "ticket__category",
  },
  {
    name: "Статус",
    key: "status_label",
    realKey: "status",
  },
  {
    name: "Дата создания",
    key: "created_at",
    type: "datetime",
  },
];

export default function PurchaseConfirmationsView({ accountRole }) {
  const meta = new AdminViewMeta({
    basePath: "/purchase-confirmations",
    nameCases: {
      first: "подтверждение об оплате",
      firstMultiple: "подтверждения об оплате",
      second: "подтверждения об оплате",
      fourth: "подтверждение об оплате",
    },
    entityListApiUrl: "/management-api/purchase-confirmations/",
    entityApiUrlPattern: "/management-api/purchase-confirmations/:id/",
    showFields: LIST_FIELDS,
    editFields: [
      {
        name: "Изображение",
        key: "image",
        type: "imageReadonly",
      },
      {
        name: "Участник",
        key: "participant_label",
        type: "readonly",
      },
      {
        name: "Статус",
        key: "status",
        type: "select",
        choices: {
          pending: "Не обработано",
          confirmed: "Оплата подтверждена",
          rejected: "Отклонено",
          refund_requested: "Запрошен возврат",
          refund_performed: "Выполнен возврат",
        },
        isRequired: true,
      },
    ],
    listFields: LIST_FIELDS,
    linkedListFields: ["id"],
    accountRole,
  });

  return <AdminView meta={meta} />;
}
