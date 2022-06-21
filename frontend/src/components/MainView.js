import clsx from "clsx";
import React from "react";

import {
  BrowserRouter as Router,
  NavLink as RouterLink,
  Route,
  Switch,
} from "react-router-dom";

import AppBar from "@material-ui/core/AppBar";
import IconButton from "@material-ui/core/IconButton";
import Link from "@material-ui/core/Link";
import Menu from "@material-ui/core/Menu";
import MenuItem from "@material-ui/core/MenuItem";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import Divider from "@material-ui/core/Divider";
import makeStyles from "@material-ui/core/styles/makeStyles";

import AccountCircle from "@material-ui/icons/AccountCircle";
import MenuIcon from "@material-ui/icons/Menu";
import MenuOpenIcon from "@material-ui/icons/MenuOpen";

import Alert from "@material-ui/lab/Alert";

import AdminAccountsView from "./admin/AdminAccountsView";
import LocationsView from "./admin/LocationsView";
import SublocationsView from "./admin/SublocationsView";
import TicketCategoriesView from "./admin/TicketCategoriesView";
import EventsView from "./admin/EventsView";
import BotsView from "./admin/BotsView";
import StaffCategoriesView from "./admin/StaffCategoriesView";
import StaffMembersView from "./admin/StaffMembersView";
import ParticipantsView from "./admin/ParticipantsView";
import GuestInvitesView from "./admin/GuestInvitesView";
import PurchaseConfirmationsView from "./admin/PurchaseConfirmationsView";
import TicketSelfiesView from "./admin/TicketSelfiesView";
import StaffInvitesView from "./admin/StaffInvitesView";
import NotificationsView from "./admin/NotificationsView";
import { MainDrawer } from "./MainDrawer";
import UnifiedPassesView from "./admin/UnifiedPassesView";
import TicketsView from "./admin/TicketsView";

function logout() {
  localStorage.removeItem("auth_token");
  window.location.reload();
}

function changePassword() {
  console.log("Trying to open change password page.");
}

const DRAWER_WIDTH = 330;

const useStyles = makeStyles((theme) => ({
  root: {
    display: "flex",
  },
  title: {
    flexGrow: 1,
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
  },
  drawer: {
    width: DRAWER_WIDTH,
    flexShrink: 0,
    whiteSpace: "nowrap",
  },
  drawerOpen: {
    width: DRAWER_WIDTH,
    transition: theme.transitions.create("width", {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  drawerClose: {
    transition: theme.transitions.create("width", {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    overflowX: "hidden",
    width: theme.spacing(7) + 1,
    [theme.breakpoints.up("sm")]: {
      width: theme.spacing(7) + 1,
    },
  },
  drawerPaper: {
    width: DRAWER_WIDTH,
  },
  drawerContainer: {
    overflow: "auto",
  },
  drawerNested: {
    paddingLeft: theme.spacing(4),
  },
  content: {
    flexGrow: 1,
    padding: theme.spacing(3),
  },
  accountEmailLabel: {
    opacity: "1 !important",
    fontWeight: 500,
  },
  menuButton: {
    marginRight: 14,
  },
  hide: {},
}));

function MainMenu(props) {
  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl);

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <div>
      <IconButton
        aria-label="account of current user"
        aria-controls="menu-appbar"
        aria-haspopup="true"
        onClick={handleMenu}
        color="inherit"
      >
        <AccountCircle />
      </IconButton>
      <Menu
        id="menu-appbar"
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
        keepMounted
        transformOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
        open={open}
        onClose={handleClose}
      >
        <MenuItem
          className={props.classes.accountEmailLabel}
          color="primary"
          disabled={true}
        >
          {props.accountEmail}
        </MenuItem>
        <Divider />
        {/*<MenuItem onClick={changePassword}>Сменить пароль</MenuItem>*/}
        <MenuItem onClick={logout}>Выйти</MenuItem>
      </Menu>
    </div>
  );
}

export default function MainView(props) {
  const classes = useStyles();
  const { accountEmail, accountRole, drawerIsOpenSaved } = props;

  const [drawerIsOpen, setDrawerOpen] = React.useState(drawerIsOpenSaved);

  const handleMenuButtonClick = () => {
    setDrawerOpen(!drawerIsOpen);
    localStorage.setItem("drawer_is_open", !drawerIsOpen);
  };

  return (
    <Router basename="/management/">
      <div className={classes.root}>
        <AppBar className={classes.appBar} position="fixed">
          <Toolbar>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              onClick={handleMenuButtonClick}
              edge="start"
              className={clsx(classes.menuButton, {
                [classes.hide]: drawerIsOpen,
              })}
            >
              {drawerIsOpen ? <MenuOpenIcon /> : <MenuIcon />}
            </IconButton>
            <Typography variant="h6" className={classes.title}>
              <Link component={RouterLink} color="inherit" to="/">
                Администрирование
              </Link>
            </Typography>
            <MainMenu
              accountEmail={accountEmail}
              accountRole={accountRole}
              classes={classes}
            />
          </Toolbar>
        </AppBar>

        <MainDrawer
          open={drawerIsOpen}
          accountRole={accountRole}
          classes={classes}
        />

        <main className={classes.content}>
          <Toolbar />
          <Switch>
            <Route path="/admin-accounts">
              <AdminAccountsView accountRole={accountRole} />
            </Route>
            <Route path="/locations">
              <LocationsView accountRole={accountRole} />
            </Route>
            <Route path="/sublocations">
              <SublocationsView accountRole={accountRole} />
            </Route>
            <Route path="/events">
              <EventsView accountRole={accountRole} />
            </Route>
            <Route path="/bots">
              <BotsView accountRole={accountRole} />
            </Route>
            <Route path="/staff-categories">
              <StaffCategoriesView accountRole={accountRole} />
            </Route>
            <Route path="/staff-members">
              <StaffMembersView accountRole={accountRole} />
            </Route>
            <Route path="/participants">
              <ParticipantsView accountRole={accountRole} />
            </Route>
            <Route path="/ticket-categories">
              <TicketCategoriesView accountRole={accountRole} />
            </Route>
            <Route path="/tickets">
              <TicketsView accountRole={accountRole} />
            </Route>
            <Route path="/guest-invites">
              <GuestInvitesView accountRole={accountRole} />
            </Route>
            <Route path="/unified-passes">
              <UnifiedPassesView accountRole={accountRole} />
            </Route>
            <Route path="/purchase-confirmations">
              <PurchaseConfirmationsView accountRole={accountRole} />
            </Route>
            <Route path="/ticket-selfies">
              <TicketSelfiesView accountRole={accountRole} />
            </Route>
            <Route path="/staff-invites">
              <StaffInvitesView accountRole={accountRole} />
            </Route>
            <Route path="/notifications">
              <NotificationsView accountRole={accountRole} />
            </Route>
            <Route path="/">
              <Alert severity="info">Выберите раздел в боковом меню.</Alert>
            </Route>
          </Switch>
        </main>
      </div>
    </Router>
  );
}
