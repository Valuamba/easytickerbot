import SupervisorAccountIcon from "@material-ui/icons/SupervisorAccount";
import { LOCATION_OWNER, ORGANIZER, SUPER_ADMIN } from "../lib/roles";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import RoomIcon from "@material-ui/icons/Room";
import PinDropIcon from "@material-ui/icons/PinDrop";
import TelegramIcon from "@material-ui/icons/Telegram";
import EventIcon from "@material-ui/icons/Event";
import AccountTreeIcon from "@material-ui/icons/AccountTree";
import LocalOfferIcon from "@material-ui/icons/LocalOffer";
import CropFreeIcon from "@material-ui/icons/CropFree";
import SupervisedUserCircleIcon from "@material-ui/icons/SupervisedUserCircle";
import DoneAllIcon from "@material-ui/icons/DoneAll";
import PhotoLibraryIcon from "@material-ui/icons/PhotoLibrary";
import PeopleIcon from "@material-ui/icons/EmojiPeople";
import GroupAddIcon from "@material-ui/icons/GroupAdd";
import AssignmentIndIcon from "@material-ui/icons/AssignmentInd";
import ChatIcon from "@material-ui/icons/Chat";
import ReceiptIcon from "@material-ui/icons/Receipt";
import React from "react";
import Drawer from "@material-ui/core/Drawer";
import clsx from "clsx";
import Toolbar from "@material-ui/core/Toolbar";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import { NavLink as RouterLink } from "react-router-dom";
import Tooltip from "@material-ui/core/Tooltip";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import ListItemText from "@material-ui/core/ListItemText";

const DRAWER_ITEMS = [
  {
    path: "/admin-accounts",
    icon: <SupervisorAccountIcon />,
    label: "Административные аккаунты",
    availableFor: [SUPER_ADMIN],
  },
  {
    label: "Локации",
    icon: <ExpandMoreIcon />,
    children: [
      {
        path: "/locations",
        icon: <RoomIcon />,
        label: "Локации",
        availableFor: [SUPER_ADMIN, LOCATION_OWNER, ORGANIZER],
      },
      {
        path: "/sublocations",
        icon: <PinDropIcon />,
        label: "Саблокации",
        availableFor: [SUPER_ADMIN, LOCATION_OWNER, ORGANIZER],
      },
    ],
  },
  {
    path: "/bots",
    icon: <TelegramIcon />,
    label: "Боты",
    availableFor: [SUPER_ADMIN, ORGANIZER],
  },
  {
    path: "/events",
    icon: <EventIcon />,
    label: "Мероприятия",
    availableFor: [SUPER_ADMIN, ORGANIZER],
  },
  {
    label: "Билеты",
    icon: <ExpandMoreIcon />,
    availableFor: [SUPER_ADMIN, ORGANIZER],
    children: [
      {
        path: "/tickets",
        icon: <LocalOfferIcon />,
        label: "Билеты",
        availableFor: [SUPER_ADMIN, ORGANIZER],
      },
      {
        path: "/ticket-categories",
        icon: <AccountTreeIcon />,
        label: "Категории билетов",
        availableFor: [SUPER_ADMIN, ORGANIZER],
      },
      {
        path: "/guest-invites",
        icon: <CropFreeIcon />,
        label: "Инвайты для гостей",
        availableFor: [SUPER_ADMIN, ORGANIZER],
      },
      {
        path: "/unified-passes",
        icon: <SupervisedUserCircleIcon />,
        label: "Универсальные пропуска",
        availableFor: [SUPER_ADMIN, ORGANIZER],
      },
      {
        path: "/purchase-confirmations",
        icon: <DoneAllIcon />,
        label: "Подтверждения об оплате",
        availableFor: [SUPER_ADMIN, ORGANIZER],
      },
      {
        path: "/ticket-selfies",
        icon: <PhotoLibraryIcon />,
        label: "Селфи",
        availableFor: [SUPER_ADMIN, ORGANIZER],
      },
    ],
  },
  {
    path: "/participants",
    icon: <PeopleIcon />,
    label: "Участники",
    availableFor: [SUPER_ADMIN, ORGANIZER],
  },
  {
    label: "Персонал",
    icon: <ExpandMoreIcon />,
    availableFor: [SUPER_ADMIN, ORGANIZER],
    children: [
      {
        path: "/staff-categories",
        icon: <GroupAddIcon />,
        label: "Категории персонала",
        availableFor: [SUPER_ADMIN, ORGANIZER],
      },
      {
        path: "/staff-invites",
        icon: <CropFreeIcon />,
        label: "Инвайты для персонала",
        availableFor: [SUPER_ADMIN, ORGANIZER],
      },
      {
        path: "/staff-members",
        icon: <AssignmentIndIcon />,
        label: "Персонал",
        availableFor: [SUPER_ADMIN, ORGANIZER],
      },
    ],
  },
  {
    path: "/notifications",
    icon: <ChatIcon />,
    label: "Уведомления",
    availableFor: [SUPER_ADMIN, ORGANIZER],
  },
  {
    path: "/tickets",
    icon: <ReceiptIcon />,
    label: "Билеты",
    availableFor: [],
  },
];

function DrawerItem(props) {
  const extraProps = props.path ? { activeClassName: "Mui-selected" } : {};
  return (
    <ListItem
      className={props.className}
      button
      component={props.path ? RouterLink : "li"}
      to={props.path}
      {...extraProps}
    >
      <Tooltip title={props.label}>
        <ListItemIcon>{props.icon}</ListItemIcon>
      </Tooltip>
      <ListItemText primary={props.label} />
    </ListItem>
  );
}

export function MainDrawer(props) {
  const { classes, open, accountRole } = props;

  function availableForFilter(item) {
    return item.availableFor ? item.availableFor.includes(accountRole) : true;
  }

  return (
    <Drawer
      variant="permanent"
      className={clsx(classes.drawer, {
        [classes.drawerOpen]: open,
        [classes.drawerClose]: !open,
      })}
      classes={{
        paper: clsx({
          [classes.drawerOpen]: open,
          [classes.drawerClose]: !open,
        }),
      }}
    >
      <Toolbar />
      <List>
        {DRAWER_ITEMS.filter(availableForFilter).map((item, i) => (
          <div key={i}>
            {(open || !item.children) && (
              <DrawerItem
                path={item.path}
                label={item.label}
                icon={item.icon}
              />
            )}
            {item.children && (
              <List component="div" disablePadding>
                {item.children.filter(availableForFilter).map((child, j) => (
                  <DrawerItem
                    className={open ? classes.drawerNested : ""}
                    key={j}
                    path={child.path}
                    label={child.label}
                    icon={child.icon}
                  />
                ))}
              </List>
            )}
          </div>
        ))}
      </List>
    </Drawer>
  );
}
