import React from "react";

import AdminView from "../_base/AdminView";
import AdminViewMeta from "../_base/AdminViewMeta";
import { ORGANIZER, SUPER_ADMIN } from "../../lib/roles";
import { renderTicketCategory } from "../../lib/render";

const LIST_FIELDS = [
  {
    name: "ID",
    key: "id",
  },
  {
    name: "Категория билетов",
    key: (i) => renderTicketCategory(i.ticket_category_data),
    realKey: "ticket_category",
  },
  {
    name: "Организатор",
    key: (i) => i.organizer_data.email,
    realKey: "organizer",
  },
  {
    name: "Дата создания",
    key: "created_at",
    type: "datetime",
  },
];

export default function GuestInvitesView({ accountRole }) {
  const meta = new AdminViewMeta({
    basePath: "/guest-invites",
    nameCases: {
      first: "Инвайт для гостей",
      firstMultiple: "Инвайты для гостей",
      second: "Инвайта для гостей",
      fourth: "Инвайт для гостей",
    },
    entityListApiUrl: "/management-api/guest-invites/",
    entityApiUrlPattern: "/management-api/guest-invites/:id/",
    showFields: LIST_FIELDS.concat([
      {
        name: "QR-код",
        key: (i) => i.qr_code_computed_data.base64_image,
        type: "qr_image",
      },
      {
        name: "Ссылка",
        key: (i) => i.qr_code_computed_data.start_url,
        type: "link",
      },
      {
        name: "Кол-во купленных билетов",
        key: "purchased_ticket_count",
      },
      {
        name: "Выручка",
        key: "purchased_ticket_sum",
      },
    ]),
    editFields: [
      {
        name: "Категория билетов",
        key: "ticket_category_data",
        realKey: "ticket_category",
        type: "autocomplete",
        fetchUrl: `/management-api/ticket-categories/`,
        toLabel: (option) => renderTicketCategory(option),
        isRequired: true,
      },
      {
        name: "Организатор",
        key: "organizer_data",
        realKey: "organizer",
        type: "autocomplete",
        fetchUrl: `/management-api/admin-accounts/?role=${ORGANIZER}`,
        toLabel: (option) => option.email,
        isRequired: true,
        availableFor: [SUPER_ADMIN],
      },
    ],
    listFields: LIST_FIELDS,
    linkedListFields: ["id"],
    processSaveData: function (formValues) {
      return {
        ticket_category: formValues.ticket_category_data
          ? formValues.ticket_category_data.id
          : null,
        organizer: formValues.organizer_data
          ? formValues.organizer_data.id
          : null,
      };
    },
    accountRole,
  });

  return <AdminView meta={meta} />;
}
