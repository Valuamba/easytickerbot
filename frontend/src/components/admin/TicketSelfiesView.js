import React from "react";

import FormControl from "@material-ui/core/FormControl";
import FormLabel from "@material-ui/core/FormLabel";

import Linkify from "react-linkify";

import AdminView from "../_base/AdminView";
import AdminViewMeta from "../_base/AdminViewMeta";
import { extractFileNameFromUrl } from "../../lib/utils";

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

function SelfieAttachment(props) {
  const { attachment } = props;

  return (
    <div>
      <a href={attachment.file} target="_blank">
        {extractFileNameFromUrl(attachment.file)}
      </a>
    </div>
  );
}

function SelfieAttachments(props) {
  const { attachments } = props;

  if (attachments.length === 0) {
    return <React.Fragment></React.Fragment>;
  }

  return (
    <FormControl fullWidth={true}>
      <FormLabel>Загруженные вложения</FormLabel>
      <div style={{ marginTop: 10, marginBottom: 10 }}>
        {attachments.map((v, i) => (
          <SelfieAttachment key={i} attachment={v} />
        ))}
      </div>
    </FormControl>
  );
}

function SelfieMessage(props) {
  const { message } = props;

  return (
    <div>
      <pre>
        <Linkify>{message.text}</Linkify>
      </pre>
    </div>
  );
}

function SelfieMessages(props) {
  const { messages } = props;

  if (messages.length === 0) {
    return <React.Fragment></React.Fragment>;
  }

  return (
    <FormControl fullWidth={true}>
      <FormLabel>Отправленные сообщения</FormLabel>
      <div style={{ marginTop: 10, marginBottom: 10 }}>
        {messages.map((v, i) => (
          <SelfieMessage key={i} message={v} />
        ))}
      </div>
    </FormControl>
  );
}

export default function TicketSelfiesView({ accountRole }) {
  const meta = new AdminViewMeta({
    basePath: "/ticket-selfies",
    nameCases: {
      first: "селфи",
      firstMultiple: "селфи",
      second: "селфи",
      fourth: "селфи",
    },
    entityListApiUrl: "/management-api/ticket-selfies/",
    entityApiUrlPattern: "/management-api/ticket-selfies/:id/",
    showFields: LIST_FIELDS.concat([
      {
        name: "Комментарий администратора для фейсконтроля",
        key: "admin_comment",
      },
    ]),
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
          confirmed: "Одобрено",
          rejected: "Отклонено",
        },
        isRequired: true,
      },
      {
        name: "Комментарий администратора для фейсконтроля",
        key: "admin_comment",
        multiline: true,
      },
    ],
    listFields: LIST_FIELDS,
    linkedListFields: ["id"],
    accountRole,
    blocks: {
      extraEditFields: (item) => (
        <React.Fragment>
          <SelfieAttachments attachments={item.attachments} />
          <SelfieMessages messages={item.messages} />
        </React.Fragment>
      ),
    },
  });

  return <AdminView meta={meta} />;
}
