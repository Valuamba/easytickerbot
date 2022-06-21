import React from "react";

import AdminView from "../_base/AdminView";
import AdminViewMeta from "../_base/AdminViewMeta";
import { ORGANIZER, SUPER_ADMIN } from "../../lib/roles";

const LIST_FIELDS = [
  {
    name: "ID",
    key: "id",
  },
  {
    name: "Бот",
    key: (i) => (i.bot_data ? i.bot_data.username : "-"),
    realKey: "bot",
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

export default function StaffInvitesView({ accountRole }) {
  const meta = new AdminViewMeta({
    basePath: "/staff-invites",
    nameCases: {
      first: "Инвайт для персонала",
      firstMultiple: "Инвайты для персонала",
      second: "Инвайта для персонала",
      fourth: "Инвайт для персонала",
    },
    entityListApiUrl: "/management-api/staff-invites/",
    entityApiUrlPattern: "/management-api/staff-invites/:id/",
    showFields: LIST_FIELDS.concat([
      {
        name: "Категории персонала",
        key: (i) =>
          (i.staff_categories_data || []).map((v) => v.name).join(", "),
      },
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
    ]),
    editFields: [
      {
        name: "Бот",
        key: "bot_data",
        realKey: "bot",
        type: "autocomplete",
        fetchUrl: `/management-api/bots/`,
        toLabel: (option) => option.username,
      },
      {
        name: "Категории персонала",
        key: "staff_categories_data",
        realKey: "staff_categories",
        type: "autocomplete",
        isMultiple: true,
        toLabel: (option) => option.name,
        fetchUrl: `/management-api/staff-categories/`,
        availableFor: [SUPER_ADMIN, ORGANIZER],
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
      const staffCategoriesData = formValues.staff_categories_data;
      return {
        bot: formValues.bot_data ? formValues.bot_data.id : null,
        staff_categories: staffCategoriesData
          ? staffCategoriesData.map((value) => value.id)
          : [],
        organizer: formValues.organizer_data
          ? formValues.organizer_data.id
          : null,
      };
    },
    accountRole,
  });

  return <AdminView meta={meta} />;
}
