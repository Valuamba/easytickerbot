import React from "react";

import AdminView from "../_base/AdminView";
import AdminViewMeta from "../_base/AdminViewMeta";
import { ORGANIZER, SUPER_ADMIN } from "../../lib/roles";
import { renderSublocationName } from "../../lib/render";

const LIST_FIELDS = [
  {
    name: "Название",
    key: "name",
  },
  {
    name: "Родительская категория",
    key: (i) => (i.parent_data ? i.parent_data.name : "-"),
    realKey: "parent",
  },
  {
    name: "Стереотип",
    key: "stereotype_label",
    realKey: "stereotype",
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

export default function StaffCategoriesView({ accountRole }) {
  const meta = new AdminViewMeta({
    basePath: "/staff-categories",
    nameCases: {
      first: "категория персонала",
      firstMultiple: "категории персонала",
      second: "категории персонала",
      fourth: "категорию персонала",
    },
    entityListApiUrl: "/management-api/staff-categories/",
    entityApiUrlPattern: "/management-api/staff-categories/:id/",
    showFields: LIST_FIELDS.concat([
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
        name: "Название",
        key: "name",
        isRequired: true,
      },
      {
        name: "Родительская категория",
        key: "parent_data",
        realKey: "parent",
        type: "autocomplete",
        fetchUrl: `/management-api/staff-categories/`,
        filterValues: (values, item) =>
          item ? values.filter((v) => v.id !== item.id) : values,
        toLabel: (option) => option.name,
      },
      {
        name: "Стереотип",
        key: "stereotype",
        type: "select",
        choices: {
          access_control: "Пропускной контроль",
        },
      },
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
    linkedListFields: ["name"],
    processSaveData: function (formValues) {
      const availableLocationsData = formValues.available_locations_data;
      const availableSublocationsData = formValues.available_sublocations_data;
      return {
        name: formValues.name,
        parent: formValues.parent_data ? formValues.parent_data.id : null,
        stereotype: formValues.stereotype,
        organizer: formValues.organizer_data
          ? formValues.organizer_data.id
          : null,
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
