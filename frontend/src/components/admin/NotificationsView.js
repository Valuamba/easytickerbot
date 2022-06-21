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
    name: "Локация",
    key: (i) => (i.location_data ? i.location_data.name : "-"),
    realKey: "location",
  },
  {
    name: "Событие",
    key: (i) => (i.event_data ? i.event_data.name : "-"),
    realKey: "event",
  },
  {
    name: "Тип",
    key: "type_label",
    realKey: "type",
  },
  {
    name: "Категория билетов",
    key: (i) =>
      i.ticket_category_data
        ? renderTicketCategory(i.ticket_category_data)
        : "-",
    realKey: "ticket_category",
  },
  {
    name: "Категория персонала",
    key: (i) => (i.staff_category_data ? i.staff_category_data.name : "-"),
    realKey: "staff_category",
  },
  {
    name: "Запланированное время отправки",
    key: "schedule_time",
    type: "datetime",
  },
  {
    name: "Отправлено",
    key: (i) => (i.was_sent ? "Да" : "Нет"),
    realKey: "was_sent",
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

export default function NotificationsView({ accountRole }) {
  const meta = new AdminViewMeta({
    basePath: "/notifications",
    nameCases: {
      first: "уведомление",
      firstMultiple: "уведомления",
      second: "уведомления",
      fourth: "уведомление",
    },
    entityListApiUrl: "/management-api/notifications/",
    entityApiUrlPattern: "/management-api/notifications/:id/",
    showFields: LIST_FIELDS.concat([
      {
        name: "Текст",
        key: "text",
      },
    ]),
    editFields: [
      {
        name: "Локация",
        key: "location_data",
        realKey: "location",
        type: "autocomplete",
        fetchUrl: `/management-api/locations/`,
        toLabel: (option) => option.name,
      },
      {
        name: "Событие",
        key: "event_data",
        realKey: "event",
        type: "autocomplete",
        fetchUrl: `/management-api/events/`,
        toLabel: (option) => option.name,
      },
      {
        name: "Тип",
        key: "type",
        type: "select",
        choices: {
          to_all: "Всем",
          to_staff: "Персоналу",
          to_guests: "Гостям",
        },
        isRequired: true,
      },
      {
        name: "Категория билетов",
        key: "ticket_category_data",
        realKey: "ticket_category",
        type: "autocomplete",
        fetchUrl: `/management-api/ticket-categories/`,
        toLabel: (option) => renderTicketCategory(option),
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
        name: "Запланированное время отправки",
        key: "schedule_time",
        type: "datetime",
      },
      {
        name: "Текст",
        key: "text",
        multiline: true,
        isRequired: true,
      },
      {
        name: "Изображение / видео",
        key: "poster",
        type: "imageupload",
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
        location: formValues.location_data ? formValues.location_data.id : null,
        event: formValues.event_data ? formValues.event_data.id : null,
        type: formValues.type,
        ticket_category: formValues.ticket_category_data
          ? formValues.ticket_category_data.id
          : null,
        staff_category: formValues.staff_category_data
          ? formValues.staff_category_data.id
          : null,
        schedule_time: formValues.schedule_time,
        text: formValues.text,
        poster: formValues.poster,
        organizer: formValues.organizer_data
          ? formValues.organizer_data.id
          : null,
      };
    },
    accountRole,
  });

  return <AdminView meta={meta} />;
}
