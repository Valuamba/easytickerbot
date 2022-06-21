import React, { useEffect, useState } from "react";

import AdminView from "../_base/AdminView";
import AdminViewMeta from "../_base/AdminViewMeta";
import { ORGANIZER, SUPER_ADMIN } from "../../lib/roles";
import Button from "@material-ui/core/Button";

import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import CircularProgress from "@material-ui/core/CircularProgress";
import DialogTitle from "@material-ui/core/DialogTitle";
import Tooltip from "@material-ui/core/Tooltip";
import TableContainer from "@material-ui/core/TableContainer";
import Table from "@material-ui/core/Table";
import TableHead from "@material-ui/core/TableHead";
import TableBody from "@material-ui/core/TableBody";
import Paper from "@material-ui/core/Paper";
import makeStyles from "@material-ui/core/styles/makeStyles";
import { callApi } from "../../lib/api";
import { SimpleTableRow } from "../../lib/tables";
import { renderLocationName } from "../../lib/render";
import Alert from "@material-ui/lab/Alert";
import { Route } from "react-router-dom";

function SendPassesDialog(props) {
  const { open, handleClose, entityId } = props;

  const [isSending, setIsSending] = useState(false);

  function handleSumbit(forceResending = false) {
    // TODO: add spinner and lock buttons while sending
    if (isSending) {
      return;
    }
    setIsSending(true);

    callApi(`/events/send-event-passes/${entityId}`, "POST", {
      force_resending: forceResending,
    })
      .then(({ data }) => {
        handleClose();
      })
      .finally(() => {
        setIsSending(false);
      });
  }

  return (
    <Dialog open={open} onClose={handleClose}>
      <DialogTitle>Отправка пропусков персоналу</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Вы можете отправить пропуска только тем учатсникам, которые их ещё не
          получили, или же всем (при этом, участники, ранее получившие пропуска,
          получат их снова).
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        {isSending && (
          <CircularProgress style={{ marginRight: 10 }} size={25} />
        )}
        <Tooltip title="Пропуска получат только те участники, которые их ещё не получили">
          <Button
            onClick={() => handleSumbit()}
            variant="contained"
            color="primary"
            autoFocus
          >
            Отправить новые
          </Button>
        </Tooltip>
        <Tooltip title="Пропуска получат все участники (в том числе те, которые ранее уже их получили)">
          <Button onClick={() => handleSumbit(true)} color="primary">
            Отправить все
          </Button>
        </Tooltip>
      </DialogActions>
    </Dialog>
  );
}

const useStyles = makeStyles((theme) => ({
  reportTable: {
    marginBottom: 21,
  },
}));

function EventReportTable(props) {
  const { data } = props;

  const classes = useStyles();

  if (!data) {
    return <div></div>;
  }

  return (
    <div>
      <TableContainer className={classes.reportTable} component={Paper}>
        <Table>
          <TableHead>
            <SimpleTableRow label="Гости" />
          </TableHead>
          <TableBody>
            <SimpleTableRow label="Всего:" value={data.visitor_count.total} />
            <SimpleTableRow label="Платных:" value={data.visitor_count.payed} />
            <SimpleTableRow
              label="Бесплатных:"
              value={data.visitor_count.free}
            />
            <SimpleTableRow
              label="Через промоутера:"
              value={data.visitor_count.promoted}
            />
            <SimpleTableRow label="Прошли:" value={data.visitor_count.passed} />
            <SimpleTableRow
              label="Не прошли (платные):"
              value={data.visitor_count.not_passed_payed}
            />
            <SimpleTableRow
              label="Не прошли (бесплатные):"
              value={data.visitor_count.not_passed_free}
            />
            <SimpleTableRow
              label="Возвраты (не включены в общие данные):"
              value={data.visitor_count.returned}
            />
          </TableBody>
        </Table>
      </TableContainer>

      <TableContainer className={classes.reportTable} component={Paper}>
        <Table>
          <TableHead>
            <SimpleTableRow label="Персонал" />
          </TableHead>
          <TableBody>
            <SimpleTableRow label="Всего:" value={data.staff_count} />
          </TableBody>
        </Table>
      </TableContainer>

      <TableContainer className={classes.reportTable} component={Paper}>
        <Table>
          <TableHead>
            <SimpleTableRow label="Выручка" />
          </TableHead>
          <TableBody>
            <SimpleTableRow label="Всего:" value={data.revenue.total} />
            <SimpleTableRow
              label="Промоутеры:"
              value={data.revenue.promoters}
            />
            <SimpleTableRow
              label="Организатор:"
              value={data.revenue.organizer}
            />
            <SimpleTableRow
              label="Сумма для возвратов непришедшим гостям:"
              value={data.revenue.to_return_unused}
            />
            <SimpleTableRow
              label="Осуществлённые возвраты (не включены в общие данные):"
              value={data.revenue.returned}
            />
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
}

function EventReportDialog(props) {
  const { open, entityId, handleClose } = props;

  const [isLoaded, setIsLoaded] = useState(false);
  const [reportData, setReportData] = useState(null);
  const reportURL = `/management-api/event-reports/${entityId}/`;
  const [flashMessage, setFlashMessage] = useState(null);

  function loadData() {
    if (!open) {
      return;
    }
    setIsLoaded(false);
    callApi(reportURL).then(({ data }) => {
      setReportData(data.report_data);
      setIsLoaded(true);
    });
  }

  useEffect(() => {
    loadData();
  }, [open]);

  function makeRefundsForUnusedTickets() {
    setIsLoaded(false);

    callApi(`/events/make-refund-for-unused-tickets/${entityId}`, "POST")
      .then(({ data }) => {
        setFlashMessage({
          severity: "info",
          text: "Средства по неиспользованным билетам возвращены.",
        });
        loadData();
      })
      .catch(() => {
        setFlashMessage({ severity: "error", text: "Произошла ошибка." });
      })
      .finally(() => {
        setIsLoaded(true);
      });
  }

  return (
    <Dialog open={open} onClose={handleClose}>
      <DialogTitle>Отчёт по событию</DialogTitle>
      <DialogContent>
        {isLoaded ? (
          <>
            {flashMessage && (
              <Alert
                severity={flashMessage.severity}
                style={{ marginBottom: 12 }}
              >
                {flashMessage.text}
              </Alert>
            )}
            <EventReportTable data={reportData} />
            <Button
              onClick={(e) => makeRefundsForUnusedTickets()}
              variant="outlined"
              color="primary"
            >
              Вернуть средства по неиспользованным билетам
            </Button>
          </>
        ) : (
          <CircularProgress style={{ marginRight: 10 }} size={25} />
        )}
      </DialogContent>
    </Dialog>
  );
}

const LIST_FIELDS = [
  {
    name: "Название",
    key: "name",
  },
  {
    name: "Дата начала",
    key: "time_start",
    type: "datetime",
  },
  {
    name: "Дата окончания",
    key: "time_end",
    type: "datetime",
  },
  {
    name: "Организатор",
    key: (i) => i.organizer_data.email,
    realKey: "organizer",
  },
  {
    name: "Бот",
    key: (i) => (i.bot_data ? i.bot_data.username : "-"),
    realKey: "bot",
  },
  {
    name: "Дата создания",
    key: "created_at",
    type: "datetime",
  },
];

export default function EventsView({ accountRole }) {
  const [isSpDialogOpen, setIsSpDialogOpen] = useState(false);
  const [isReportDialogOpen, setIsReportDialogOpen] = useState(false);

  const meta = new AdminViewMeta({
    basePath: "/events",
    nameCases: {
      first: "мероприятие",
      firstMultiple: "мероприятия",
      second: "мероприятия",
      fourth: "мероприятие",
    },
    entityListApiUrl: "/management-api/events/",
    entityApiUrlPattern: "/management-api/events/:id/",
    showFields: LIST_FIELDS.concat([
      {
        name: "Категории персонала",
        key: (i) =>
          (i.staff_categories_data || []).map((v) => v.name).join(", "),
      },
    ]),
    editFields: [
      {
        name: "Название",
        key: "name",
        isRequired: true,
      },
      {
        name: "Постер",
        key: "poster",
        type: "imageupload",
      },
      {
        name: "Дата начала",
        key: "time_start",
        type: "datetime",
        isRequired: true,
      },
      {
        name: "Дата окончания",
        key: "time_end",
        type: "datetime",
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
      {
        name: "Бот",
        key: "bot_data",
        realKey: "bot",
        type: "autocomplete",
        fetchUrl: `/management-api/bots/`,
        toLabel: (option) => option.username,
        availableFor: [SUPER_ADMIN, ORGANIZER],
      },
      {
        name: "Локации",
        key: "locations_data",
        realKey: "locations",
        type: "autocomplete",
        isMultiple: true,
        toLabel: (option) => renderLocationName(option),
        fetchUrl: `/management-api/locations/`,
        availableFor: [SUPER_ADMIN, ORGANIZER],
        isRequired: true,
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
        name: "Тип оплаты",
        key: "payment_type",
        type: "select",
        choices: {
          fondy: "Fondy",
          yoomoney: "YooMoney",
          yoomoney_telegram: "YooMoney (Telegram)",
        },
      },
    ],
    listFields: LIST_FIELDS,
    linkedListFields: ["name"],
    processSaveData: function (formValues) {
      const locationsData = formValues.locations_data;
      const staffCategoriesData = formValues.staff_categories_data;
      return {
        name: formValues.name,
        time_start: formValues.time_start,
        time_end: formValues.time_end,
        organizer: formValues.organizer_data
          ? formValues.organizer_data.id
          : null,
        bot: formValues.bot_data ? formValues.bot_data.id : null,
        poster: formValues.poster,
        payment_type: formValues.payment_type,
        locations: locationsData ? locationsData.map((value) => value.id) : [],
        staff_categories: staffCategoriesData
          ? staffCategoriesData.map((value) => value.id)
          : [],
      };
    },
    blocks: {
      extraShowControls: (entityId) => (
        <div>
          <Button
            onClick={(e) => setIsReportDialogOpen(true)}
            variant="outlined"
            color="primary"
            style={{ marginRight: 10 }}
          >
            Показать отчёт
          </Button>
          <EventReportDialog
            open={isReportDialogOpen}
            handleClose={(e) => setIsReportDialogOpen(false)}
            entityId={entityId}
          />

          <Button
            onClick={(e) => setIsSpDialogOpen(true)}
            variant="outlined"
            color="primary"
            style={{ marginRight: 10 }}
          >
            Отправить пропуска для персонала
          </Button>
          <SendPassesDialog
            open={isSpDialogOpen}
            handleClose={(e) => setIsSpDialogOpen(false)}
            entityId={entityId}
          />
        </div>
      ),
    },
    accountRole,
  });

  return <AdminView meta={meta} />;
}
