import LightningDatatable from "lightning/datatable";
import badgeCell from "./badgeCell.html";

export default class CustomDatatableWithBadges extends LightningDatatable {
  static customTypes = {
    badge: {
      template: badgeCell,
      standardCellLayout: true
    }
  };
}