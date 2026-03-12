import { LightningElement, track, api } from "lwc";

export default class F003RgV9950HonkenJokenTanpo extends LightningElement {
    activeSections = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r"];
    activeSectionsMessage = "";
    isAllVisible = true;

    @track reviewNumber = "0313";
    @track amountUnit = "〇〇〇";
    @track groupNumber = "9";
    @track date = "2025/3/31";
}
