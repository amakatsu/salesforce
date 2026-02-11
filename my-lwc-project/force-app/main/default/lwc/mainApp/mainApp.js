import { LightningElement, track } from "lwc";

export default class MainApp extends LightningElement {
  @track currentPage = "search";
  @track selectedUserId = null;
  @track previousPage = null;

  // 通知システム
  @track showNotification = false;
  @track notificationMessage = "";
  @track notificationType = "info"; // success, error, warning, info

  // ページ判定用のgetter
  get isSearchPage() {
    return this.currentPage === "search";
  }

  get isProfileViewPage() {
    return this.currentPage === "profile-view";
  }

  get isProfileEditPage() {
    return this.currentPage === "profile-edit";
  }

  get isSettingsPage() {
    return this.currentPage === "settings";
  }

  get hasActivePage() {
    return ["search", "profile-view", "profile-edit", "settings"].includes(
      this.currentPage
    );
  }

  // 通知用のgetter
  get notificationClass() {
    const baseClass = "slds-notify slds-notify_toast";
    switch (this.notificationType) {
      case "success":
        return `${baseClass} slds-theme_success`;
      case "error":
        return `${baseClass} slds-theme_error`;
      case "warning":
        return `${baseClass} slds-theme_warning`;
      default:
        return `${baseClass} slds-theme_info`;
    }
  }

  get notificationIcon() {
    switch (this.notificationType) {
      case "success":
        return "utility:success";
      case "error":
        return "utility:error";
      case "warning":
        return "utility:warning";
      default:
        return "utility:info";
    }
  }

  // 初期化
  connectedCallback() {
    this.currentPage = "search"; // デフォルトはメンバー検索ページ
  }

  // ナビゲーション処理
  handleNavigation(event) {
    console.log("handleNavigation called with event:", event.detail);
    const { page, userId } = event.detail;
    this.previousPage = this.currentPage;
    this.currentPage = page;

    if (userId) {
      this.selectedUserId = userId;
    }

    console.log("Navigate to:", page, "UserId:", userId);
    console.log(
      "Current state - currentPage:",
      this.currentPage,
      "selectedUserId:",
      this.selectedUserId
    );
  }

  // 戻るボタン処理
  handleGoBack() {
    if (this.previousPage) {
      this.currentPage = this.previousPage;
      this.previousPage = null;
    } else {
      // デフォルトで検索ページに戻る
      this.currentPage = "search";
    }
    this.selectedUserId = null;
  }

  // 検索開始
  handleStartSearch() {
    this.currentPage = "search";
  }

  // プロフィール表示
  handleViewProfile(event) {
    const userId = event.detail.userId || event.detail.memberId;
    this.selectedUserId = userId;
    this.previousPage = this.currentPage;
    this.currentPage = "profile-view";

    console.log("View profile for user:", userId);
  }

  // プロフィール編集
  handleEditProfile(event) {
    const userId = event.detail.userId || event.detail.memberId;
    this.selectedUserId = userId;
    this.previousPage = this.currentPage;
    this.currentPage = "profile-edit";

    console.log("Edit profile for user:", userId);
  }

  // メッセージ送信
  handleSendMessage(event) {
    const userId = event.detail.userId || event.detail.memberId;
    this.showNotification("メッセージ機能は開発中です", "info");

    console.log("Send message to user:", userId);
  }

  // プロフィール保存完了
  handleProfileSave(event) {
    this.showNotification("プロフィールが正常に保存されました", "success");

    // ヘッダーの現在ユーザー情報を更新
    const headerComponent = this.template.querySelector("c-app-header");
    if (headerComponent) {
      headerComponent.loadCurrentUser();
    }

    this.handleGoBack();
  }

  // ログアウト処理
  handleLogout() {
    this.showNotification("ログアウトしました", "info");
    this.currentPage = "search";
    this.selectedUserId = null;
    this.previousPage = null;

    // TODO: 実際のログアウト処理を実装
    console.log("ログアウト処理");
  }

  // 通知表示
  showNotification(message, type = "info") {
    this.notificationMessage = message;
    this.notificationType = type;
    this.showNotification = true;

    // 3秒後に自動で閉じる
    setTimeout(() => {
      this.showNotification = false;
    }, 3000);
  }

  // 通知を閉じる
  dismissNotification() {
    this.showNotification = false;
  }
}
