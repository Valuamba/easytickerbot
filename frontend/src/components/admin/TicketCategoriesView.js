import React from "react";

import AdminView from "../_base/AdminView";
import AdminViewMeta from "../_base/AdminViewMeta";
import { renderSublocationName } from "../../lib/render";

const LIST_FIELDS = [
  {
    name: "Название",
    key: "name",
  },
  {
    name: "Событие",
    key: (i) => i.event_data.name,
    realKey: "event",
  },
  {
    name: "Стоимость",
    key: "base_price",
  },
  {
    name: "Максимальное количество билетов",
    key: "max_ticket_count",
  },
  {
    name: "Осталось билетов",
    key: "available_ticket_count",
    disableOrdering: true,
  },
  {
    name: "Лимит покупки билетов для одного участника",
    key: "per_participant_limit",
  },
  {
    name: "Ручное подтверждение",
    key: (i) => (i.with_manual_confirmation ? "Да" : "Нет"),
    realKey: "with_manual_confirmation",
  },
  {
    name: "Требуется селфи",
    key: (i) => (i.selfie_required ? "Да" : "Нет"),
    realKey: "selfie_required",
  },
  {
    name: "Активна",
    key: (i) => (i.is_active ? "Да" : "Нет"),
    realKey: "is_active",
  },
  {
    name: "Скрытая",
    key: (i) => (i.is_hidden ? "Да" : "Нет"),
    realKey: "is_hidden",
  },
  {
    name: "Дата создания",
    key: "created_at",
    type: "datetime",
  },
];

export default function TicketCategoriesView({ accountRole }) {
  const meta = new AdminViewMeta({
    basePath: "/ticket-categories",
    nameCases: {
      first: "категория билетов",
      firstMultiple: "категории билетов",
      second: "категории билетов",
      fourth: "категорию билетов",
    },
    entityListApiUrl: "/management-api/ticket-categories/",
    entityApiUrlPattern: "/management-api/ticket-categories/:id/",
    showFields: LIST_FIELDS.concat([
      {
        name: "Описание",
        key: "description",
      },
      {
        name: "Доступные локации",
        key: (i) =>
          (i.available_locations_data || []).map((v) => v.name).join(", "),
      },
      {
        name: "Доступные саблокации",
        key: (i) =>
          (i.available_sublocations_data || [])
            .map((v) => renderSublocationName(v))
            .join(", "),
      },
    ]),
    editFields: [
      {
        name: "Событие",
        key: "event_data",
        realKey: "event",
        type: "autocomplete",
        fetchUrl: `/management-api/events/`,
        toLabel: (option) => option.name,
        isRequired: true,
      },
      {
        name: "Название",
        key: "name",
        isRequired: true,
      },
      {
        name: "Описание",
        key: "description",
      },
      {
        name: "Стоимость",
        key: "base_price",
        type: "number",
        isRequired: true,
      },
      {
        name: "Максимальное количество билетов",
        key: "max_ticket_count",
        type: "number",
        isRequired: true,
      },
      {
        name: "Лимит покупки билетов для одного участника",
        key: "per_participant_limit",
        type: "number",
        isRequired: true,
      },
      // TODO: filter by event
      {
        name: "Доступные локации",
        key: "available_locations_data",
        realKey: "available_locations",
        type: "autocomplete",
        isMultiple: true,
        toLabel: (option) => option.name,
        fetchUrl: `/management-api/locations/`,
      },
      {
        name: "Доступные саблокации",
        key: "available_sublocations_data",
        realKey: "available_sublocations",
        type: "autocomplete",
        isMultiple: true,
        toLabel: (option) => renderSublocationName(option),
        fetchUrl: `/management-api/sublocations/`,
      },
      {
        name: "Запрос дополнительных данных",
        key: "additional_data_request",
        multiline: true,
        hint:
          'Например: "Отправьте скан паспорта и ссылку на страницу вконтакте."',
      },
      {
        name: "Быстрый запрос одного текстового поля",
        type: "checkbox",
        key: "additional_data_short_request",
      },
      {
        name: "Текст после подтверждения селфи",
        key: "selfie_confirmed_text",
        multiline: true,
        hint: 'По умолчанию: "Селфи подтверждено."',
      },
      {
        name: "Дата окончания действия",
        key: "lifetime_end",
        type: "datetime",
      },
      {
        name: "Ручное подтверждение",
        key: "with_manual_confirmation",
        type: "checkbox",
      },
      {
        name: "Требуется селфи",
        key: "selfie_required",
        type: "checkbox",
      },
      {
        name: "Не требовать селфи, если загружено ранее",
        key: "avoid_selfie_reconfirmation",
        type: "checkbox",
      },
      {
        name: "Активна",
        key: "is_active",
        type: "checkbox",
      },
      {
        name: "Скрытая",
        key: "is_hidden",
        type: "checkbox",
      },
    ],
    listFields: LIST_FIELDS,
    linkedListFields: ["name"],
    processSaveData: function (formValues) {
      const availableLocationsData = formValues.available_locations_data;
      const availableSublocationsData = formValues.available_sublocations_data;
      return {
        name: formValues.name,
        description: formValues.description,
        event: formValues.event_data ? formValues.event_data.id : null,
        base_price: formValues.base_price,
        max_ticket_count: formValues.max_ticket_count,
        per_participant_limit: formValues.per_participant_limit,
        with_manual_confirmation: formValues.with_manual_confirmation,
        selfie_required: formValues.selfie_required,
        avoid_selfie_reconfirmation: formValues.avoid_selfie_reconfirmation,
        time_end: formValues.time_end,
        is_active: formValues.is_active,
        is_hidden: formValues.is_hidden,
        selfie_confirmed_text: formValues.selfie_confirmed_text,
        additional_data_request: formValues.additional_data_request,
        additional_data_short_request: formValues.additional_data_short_request,
        available_locations: availableLocationsData
          ? availableLocationsData.map((value) => value.id)
          : [],
        available_sublocations: availableSublocationsData
          ? availableSublocationsData.map((value) => value.id)
          : [],
      };
    },
    accountRole,
  });

  return <AdminView meta={meta} />;
}
