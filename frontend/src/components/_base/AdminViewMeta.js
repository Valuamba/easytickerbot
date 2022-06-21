import { capitalize } from "lodash/string";

import React from "react";

import { generatePath, Link as RouterLink } from "react-router-dom";

import Typography from "@material-ui/core/Typography";
import Breadcrumbs from "@material-ui/core/Breadcrumbs";
import Link from "@material-ui/core/Link";

function AdminViewBreadcrumbs(props) {
  return (
    <Breadcrumbs>
      <Link component={RouterLink} to="/">
        Администрирование
      </Link>
      {props.listHref ? (
        <Link component={RouterLink} to={props.listHref}>
          {capitalize(props.listTitle)}
        </Link>
      ) : (
        <Typography color="textPrimary">
          {capitalize(props.listTitle)}
        </Typography>
      )}
      {props.children}
    </Breadcrumbs>
  );
}

export default class AdminViewMeta {
  constructor({
    basePath,
    nameCases,
    entityApiUrlPattern,
    entityListApiUrl,
    showFields,
    editFields,
    listFields,
    linkedListFields,
    processSaveData,
    blocks,
    accountRole,
    editingDisabled,
  }) {
    this.basePath = basePath;
    this.addPath = `${basePath}/add`;
    this.showPathPattern = `${basePath}/:id`;
    this.editPathPattern = `${basePath}/:id/edit`;
    this.deletePathPattern = `${basePath}/:id/delete`;

    this.nameCases = nameCases;

    this.entityApiUrlPattern = entityApiUrlPattern;
    this.entityListApiUrl = entityListApiUrl;

    this.showFields = showFields;
    this.editFields = editFields;
    this.listFields = listFields;
    this.linkedListFields = linkedListFields;

    this.processSaveData = processSaveData;

    this.blocks = blocks || {};

    this.accountRole = accountRole;

    this.editingDisabled = editingDisabled || false;
  }

  getEditFields() {
    return this.editFields.filter((field) =>
      field.availableFor ? field.availableFor.includes(this.accountRole) : true
    );
  }

  createSaveData(formValues) {
    if (this.processSaveData) {
      return this.processSaveData(formValues);
    }
    return formValues;
  }

  getEntityApiUrl(entityId) {
    return generatePath(this.entityApiUrlPattern, { id: entityId });
  }

  getListPath() {
    return this.basePath;
  }

  getAddPath() {
    return this.addPath;
  }

  getShowPath(entityId) {
    return generatePath(this.showPathPattern, { id: entityId });
  }

  getEditPath(entityId) {
    return generatePath(this.editPathPattern, { id: entityId });
  }

  getDeletePath(entityId) {
    return generatePath(this.deletePathPattern, { id: entityId });
  }

  getShowLink(entityId) {
    return (
      <Link component={RouterLink} to={this.getShowPath(entityId)}>
        #{entityId}
      </Link>
    );
  }

  getListBreadcrumbs() {
    return <AdminViewBreadcrumbs listTitle={this.nameCases.firstMultiple} />;
  }

  getAddBreadcrumbs() {
    return (
      <AdminViewBreadcrumbs
        listTitle={this.nameCases.firstMultiple}
        listHref={this.getListPath()}
      >
        <Typography color="textPrimary">Добавить</Typography>
      </AdminViewBreadcrumbs>
    );
  }

  getShowBreadcrumbs(entityId) {
    return (
      <AdminViewBreadcrumbs
        listTitle={this.nameCases.firstMultiple}
        listHref={this.getListPath()}
      >
        <Typography color="textPrimary">#{entityId}</Typography>
      </AdminViewBreadcrumbs>
    );
  }

  getEditBreadcrumbs(entityId) {
    return (
      <AdminViewBreadcrumbs
        listTitle={this.nameCases.firstMultiple}
        listHref={this.getListPath()}
      >
        {this.getShowLink(entityId)}
        <Typography color="textPrimary">Редактирование</Typography>
      </AdminViewBreadcrumbs>
    );
  }

  getDeleteBreadcrumbs(entityId) {
    return (
      <AdminViewBreadcrumbs
        listTitle={this.nameCases.firstMultiple}
        listHref={this.getListPath()}
      >
        {this.getShowLink(entityId)}
        <Typography color="textPrimary">Удаление</Typography>
      </AdminViewBreadcrumbs>
    );
  }

  getBlocks() {
    return this.blocks;
  }
}
