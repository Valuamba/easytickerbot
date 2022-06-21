import React from "react";

import AdminView from "../_base/AdminView";
import AdminViewMeta from "../_base/AdminViewMeta";
import { ORGANIZER, SUPER_ADMIN } from "../../lib/roles";
import { renderSublocationName } from "../../lib/render";

function getParticipantLabel(i) {
  return i.participant_data.label;
}

const LIST_FIELDS = [
  {
    name: "Участник",
    key: getParticipantLabel,
    realKey: "participant",
  },
  {
    name: "Telegram ID",
    key: (i) => i.participant_data.telegram_id,
    realKey: "participant__telegram_id",
  },
  {
    name: "Организатор",
    key: (i) => (i.organizer_data ? i.organizer_data.email : "-"),
    realKey: "organizer",
  },
  {
    name: "Категория персонала",
    key: (i) => (i.staff_category_data ? i.staff_category_data.name : "-"),
    realKey: "staff_category",
  },
  {
    name: "Подтверждён",
    key: (i) => (i.is_approved ? "Да" : "Нет"),
    realKey: "is_approved",
  },
];

export default function StaffMembersView({ accountRole }) {
  const meta = new AdminViewMeta({
    basePath: "/staff-members",
    nameCases: {
      first: "персонал",
      firstMultiple: "персонал",
      second: "персонала",
      fourth: "персонал",
    },
    entityListApiUrl: "/management-api/staff-members/",
    entityApiUrlPattern: "/management-api/staff-members/:id/",
    showFields: LIST_FIELDS.concat([
      {
        name: "Дата создания",
        key: "created_at",
        type: "datetime",
      },
    ]),
    editFields: [
      {
        name: "Участник",
        key: "participant_data",
        realKey: "participant",
        type: "autocomplete",
        fetchUrl: `/management-api/participants/`,
        toLabel: (option) => option.label,
        isRequired: true,
      },
      {
        name: "Категория персонала",
        key: "staff_category_data",
        realKey: "staff_category",
        type: "autocomplete",
        fetchUrl: `/management-api/staff-categories/`,
        toLabel: (option) => option.name,
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
      {
        name: "Подтверждён",
        key: "is_approved",
        type: "checkbox",
      },
      {
        type: "divider",
      },
      {
        name: "Пропускной контроль: текущее мероприятие",
        key: "current_access_control_event_data",
        realKey: "current_access_control_event",
        type: "autocomplete",
        toLabel: (option) => `${option.name} (${option.organizer_data.email})`,
        fetchUrl: `/management-api/events/`,
        availableFor: [SUPER_ADMIN, ORGANIZER],
      },
      {
        name: "Пропускной контроль: текущая локация",
        key: "current_access_control_location_data",
        realKey: "current_access_control_location",
        type: "autocomplete",
        toLabel: (option) => option.name,
        fetchUrl: `/management-api/locations/`,
        availableFor: [SUPER_ADMIN, ORGANIZER],
      },
      {
        name: "Пропускной контроль: текущая саблокация",
        key: "current_access_control_sublocation_data",
        realKey: "current_access_control_sublocation",
        type: "autocomplete",
        toLabel: (option) => renderSublocationName(option),
        fetchUrl: `/management-api/sublocations/`,
        availableFor: [SUPER_ADMIN, ORGANIZER],
      },
    ],
    listFields: LIST_FIELDS,
    linkedListFields: [getParticipantLabel],
    processSaveData: function (formValues) {
      return {
        participant: formValues.participant_data
          ? formValues.participant_data.id
          : null,
        staff_category: formValues.staff_category_data
          ? formValues.staff_category_data.id
          : null,
        organizer: formValues.organizer_data
          ? formValues.organizer_data.id
          : null,
        is_approved: formValues.is_approved,
        current_access_control_event: formValues.current_access_control_event_data
          ? formValues.current_access_control_event_data.id
          : null,
        current_access_control_location: formValues.current_access_control_location_data
          ? formValues.current_access_control_location_data.id
          : null,
        current_access_control_sublocation: formValues.current_access_control_sublocation_data
          ? formValues.current_access_control_sublocation_data.id
          : null,
      };
    },
    accountRole,
  });

  return <AdminView meta={meta} />;
}
