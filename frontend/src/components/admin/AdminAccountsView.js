import React from "react";

import AdminView from "../_base/AdminView";
import AdminViewMeta from "../_base/AdminViewMeta";
import { ORGANIZER, SUPER_ADMIN } from "../../lib/roles";

const listFields = [
  {
    name: "Email",
    key: "email",
  },
  {
    name: "Роль",
    key: "role_label",
    realKey: "role",
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
    name: "Активен",
    key: (i) => (i.is_active ? "Да" : "Нет"),
    realKey: "is_active",
  },
];

export default function AdminAccountsView({ accountRole }) {
  const meta = new AdminViewMeta({
    basePath: "/admin-accounts",
    entityListApiUrl: "/management-api/admin-accounts/",
    entityApiUrlPattern: "/management-api/admin-accounts/:id/",
    nameCases: {
      first: "административный аккаунт",
      firstMultiple: "административные аккаунты",
      second: "административного аккаунта",
      fourth: "административный аккаунт",
    },
    showFields: listFields.concat([
      {
        name: "Telegram ID",
        key: (i) => (i.telegram_id ? i.telegram_id : "-"),
      },
      {
        name: "Бот для уведомлений",
        key: (i) =>
          i.notification_bot_data ? i.notification_bot_data.username : "-",
      },
      {
        name: "Дата создания",
        key: "date_joined",
        type: "datetime",
      },
    ]),
    editFields: [
      {
        name: "Email",
        key: "email",
        isRequired: true,
      },
      {
        name: "Роль",
        key: "role",
        type: "select",
        choices: {
          organizer: "Организатор",
          location_owner: "Владелец локации",
          super_admin: "Суперадмин",
        },
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
        name: "Telegram ID",
        key: "telegram_id",
      },
      {
        name: "Бот для уведомлений",
        key: "notification_bot_data",
        realKey: "notification_bot",
        type: "autocomplete",
        fetchUrl: `/management-api/bots/`,
        toLabel: (option) => option.username,
        availableFor: [SUPER_ADMIN, ORGANIZER],
      },
      {
        name: "Токен интеграции Telegram с ЮКассой",
        key: "organizer_telegram_checkout_token",
      },
      {
        name: "ID магазина (ЮКасса)",
        key: "organizer_shop_id",
      },
      {
        name: "Секретный ключ магазина (ЮКасса)",
        key: "organizer_shop_secret",
      },
      {
        name: "Merchant ID (Fondy)",
        key: "organizer_fondy_merchant_id",
      },
      {
        name: "Payment key (Fondy)",
        key: "organizer_fondy_merchant_password",
      },
      {
        name: "Активен",
        key: "is_active",
        type: "checkbox",
      },
      {
        name: "Новый пароль",
        key: "new_password",
        type: "password",
      },
      {
        name: "Подтверждение пароля",
        key: "new_password_confirmation",
        type: "password",
      },
    ],
    listFields: listFields,
    linkedListFields: ["email"],
    processSaveData: function (formValues) {
      return {
        email: formValues.email,
        role: formValues.role,
        first_name: formValues.first_name,
        last_name: formValues.last_name,
        telegram_id: formValues.telegram_id,
        organizer_telegram_checkout_token:
          formValues.organizer_telegram_checkout_token,
        organizer_shop_id: formValues.organizer_shop_id,
        organizer_shop_secret: formValues.organizer_shop_secret,
        organizer_fondy_merchant_id: formValues.organizer_fondy_merchant_id,
        organizer_fondy_merchant_password:
          formValues.organizer_fondy_merchant_password,
        notification_bot: formValues.notification_bot_data
          ? formValues.notification_bot_data.id
          : null,
        is_active: formValues.is_active,
        new_password: formValues.new_password,
        new_password_confirmation: formValues.new_password_confirmation,
      };
    },
    accountRole,
  });

  return <AdminView meta={meta} />;
}
