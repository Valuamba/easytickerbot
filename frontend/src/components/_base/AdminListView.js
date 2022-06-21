import { capitalize } from "lodash/string";

import React, { useEffect, useState } from "react";

import { Link as RouterLink, useHistory } from "react-router-dom";

import Link from "@material-ui/core/Link";
import Tooltip from "@material-ui/core/Tooltip";
import IconButton from "@material-ui/core/IconButton";
import Fab from "@material-ui/core/Fab";
import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography";
import TableContainer from "@material-ui/core/TableContainer";
import Paper from "@material-ui/core/Paper";
import Table from "@material-ui/core/Table";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import TableCell from "@material-ui/core/TableCell";
import TableSortLabel from "@material-ui/core/TableSortLabel";
import TableBody from "@material-ui/core/TableBody";
import makeStyles from "@material-ui/core/styles/makeStyles";
import { fade } from "@material-ui/core/styles";
import Pagination from "@material-ui/lab/Pagination";
import PaginationItem from "@material-ui/lab/PaginationItem";
import InputBase from "@material-ui/core/InputBase";

import AddIcon from "@material-ui/icons/Add";
import EditIcon from "@material-ui/icons/Edit";
import SearchIcon from "@material-ui/icons/Search";

import { callApi } from "../../lib/api";

import { renderValue } from "./view";

const useStyles = makeStyles((theme) => ({
  titleContainer: {
    display: "flex",
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(2),
  },
  title: {
    flexGrow: 1,
  },
  table: {
    minWidth: 650,
  },
  fab: {
    position: "fixed",
    bottom: theme.spacing(3),
    right: theme.spacing(3),
  },
  linkedField: {
    textTransform: "none",
  },
  search: {
    position: "relative",
    borderRadius: theme.shape.borderRadius,
    backgroundColor: fade(theme.palette.common.white, 0.15),
    "&:hover": {
      backgroundColor: fade(theme.palette.common.white, 0.25),
    },
    marginLeft: 0,
    width: "100%",
    [theme.breakpoints.up("sm")]: {
      width: "auto",
    },
  },
  searchIcon: {
    padding: theme.spacing(0, 1),
    height: "100%",
    position: "absolute",
    pointerEvents: "none",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 2,
  },
  inputRoot: {
    color: "inherit",
  },
  inputInput: {
    padding: theme.spacing(1, 1, 1, 0),
    // vertical padding + font size from searchIcon
    paddingLeft: `calc(1em + ${theme.spacing(3)}px)`,
    transition: theme.transitions.create("width"),
    width: "100%",
    [theme.breakpoints.up("md")]: {
      width: "20ch",
    },
    background: "#eee",
  },
}));

function ItemListHeaderCell(props) {
  const { item, basePath, page, orderBy, search } = props;

  const orderKey = item.disableOrdering
    ? undefined
    : item.realKey || (typeof item.key === "function" ? undefined : item.key);
  const isActive = orderKey === (orderBy || "").replace("-", "");
  const currentDirection = (orderBy || "").startsWith("-") ? "desc" : "asc";
  const directedOrderKey =
    currentDirection === "asc" ? `-${orderKey}` : orderKey;

  return (
    <TableCell>
      <TableSortLabel active={isActive} direction={currentDirection}>
        {orderKey ? (
          <Link
            component={RouterLink}
            color="inherit"
            to={buildListFetchUrl(basePath, page, directedOrderKey, search)}
          >
            {item.name}
          </Link>
        ) : (
          item.name
        )}
      </TableSortLabel>
    </TableCell>
  );
}

function ListSearch(props) {
  const { classes, basePath, page, orderBy, search } = props;

  const [value, setValue] = useState(search || "");

  const history = useHistory();

  const handleSubmit = (event) => {
    event.preventDefault();
    const targetUrl = buildListFetchUrl(basePath, page, orderBy, value);
    history.push(targetUrl);
  };

  const handleInputChange = (event) => {
    event.preventDefault();
    setValue(event.target.value);
  };

  return (
    <div className={classes.search}>
      <div className={classes.searchIcon}>
        <SearchIcon />
      </div>
      <form onSubmit={handleSubmit}>
        <InputBase
          placeholder="Поиск"
          classes={{
            root: classes.inputRoot,
            input: classes.inputInput,
          }}
          onChange={handleInputChange}
          value={value}
        />
      </form>
    </div>
  );
}

function ItemList(props) {
  const { classes, meta, items, basePath, page, orderBy, search } = props;

  if (!Array.isArray(items) || !items.length) {
    return <div>Не найдено ни одной записи.</div>;
  }

  return (
    <TableContainer component={Paper}>
      <Table className={classes.table}>
        <TableHead>
          <TableRow>
            {meta.listFields.map((item, i) => (
              <ItemListHeaderCell
                key={i}
                item={item}
                basePath={basePath}
                page={page}
                orderBy={orderBy}
                search={search}
              />
            ))}
            <TableCell align="right"></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {items.map((item, i) => (
            <TableRow key={i}>
              {meta.listFields.map((field, i) => (
                <TableCell key={i}>
                  {meta.linkedListFields.includes(field.key) ? (
                    <Button
                      className={classes.linkedField}
                      component={RouterLink}
                      to={meta.getShowPath(item.id)}
                      color="primary"
                    >
                      {renderValue(item, field)}
                    </Button>
                  ) : (
                    renderValue(item, field)
                  )}
                </TableCell>
              ))}
              <TableCell align="right">
                {!meta.editingDisabled && (
                  <Tooltip title="Редактировать">
                    <IconButton
                      component={RouterLink}
                      to={meta.getEditPath(item.id)}
                      size="small"
                    >
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

function ListPagination(props) {
  const { basePath, total, page, orderBy, search } = props;

  const pageSize = 20;
  const pageCount = Math.ceil(total / pageSize);

  if (!pageCount || pageCount <= 1) {
    return <React.Fragment></React.Fragment>;
  }

  return (
    <Pagination
      style={{ marginTop: 21 }}
      size="large"
      count={pageCount}
      page={page}
      renderItem={(item) => (
        <PaginationItem
          component={RouterLink}
          to={buildListFetchUrl(basePath, item.page, orderBy, search)}
          {...item}
        />
      )}
    />
  );
}

function buildListFetchUrl(baseUrl, page, orderBy, search) {
  const params = {};

  if (page !== 1) {
    params["page"] = page;
  }

  if (orderBy) {
    params["order_by"] = orderBy;
  }

  if (search) {
    params["search"] = search;
  }

  const searchStr = new URLSearchParams(params).toString();

  return `${baseUrl}${searchStr ? "?" + searchStr : ""}`;
}

export default function AdminListView(props) {
  const { meta } = props;

  const query = new URLSearchParams(location.search);
  const page = parseInt(query.get("page") || "1", 10);
  const orderBy = query.get("order_by");
  const search = query.get("search");

  const [isLoaded, setIsLoaded] = useState(false);
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [pageNotFound, setPageNotFound] = useState(false);

  const classes = useStyles();

  useEffect(() => {
    const listUrl = buildListFetchUrl(
      meta.entityListApiUrl,
      page,
      orderBy,
      search
    );

    callApi(listUrl).then(({ data, response }) => {
      setPageNotFound(response.status === 404);
      setItems(data["results"]);
      setTotal(data["count"]);
      setIsLoaded(true);
    });
  }, [page, orderBy, search, pageNotFound]);

  if (!isLoaded) {
    return <div></div>;
  }

  if (pageNotFound) {
    return <div>Страница не найдена.</div>;
  }

  const listPath = meta.getListPath();

  return (
    <div>
      {/* Breadcrumbs */}
      {meta.getListBreadcrumbs()}

      <div className={classes.titleContainer}>
        {/* Title */}
        <Typography className={classes.title} component="h1" variant="h5">
          {capitalize(meta.nameCases.firstMultiple)}
        </Typography>

        {/* List search */}
        <ListSearch
          classes={classes}
          basePath={listPath}
          page={page}
          orderBy={orderBy}
          search={search}
        />
      </div>

      {/* Item list */}
      <ItemList
        meta={meta}
        classes={classes}
        items={items}
        basePath={listPath}
        page={page}
        orderBy={orderBy}
        search={search}
      />

      {/* Pagination */}
      <ListPagination
        items={items}
        total={total}
        basePath={listPath}
        page={page}
        orderBy={orderBy}
        search={search}
      />

      <Tooltip title="Добавить">
        <Fab
          component={RouterLink}
          className={classes.fab}
          color="primary"
          to={meta.getAddPath()}
        >
          <AddIcon />
        </Fab>
      </Tooltip>
    </div>
  );
}
