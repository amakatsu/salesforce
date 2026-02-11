import { LightningElement, track, api } from "lwc";
import getUserProfile from "@salesforce/apex/UserProfileService.getUserProfile";

export default class AppHeader extends LightningElement {
  @track showUserMenu = false;
  @track currentUser = {
    id: "current-user",
    name: "Current User",
    email: "user@example.com",
    photo: null
  };

  @api currentPage = "search";

  connectedCallback() {
    // 現在のユーザー情報を取得
    this.loadCurrentUser();

    // バウンドされたハンドラーを保存
    this.boundHandleDocumentClick = this.handleDocumentClick.bind(this);
  }

  renderedCallback() {
    if (!this.documentClickListenerAdded) {
      // ドキュメントクリックイベントを追加してメニューを閉じる
      document.addEventListener("click", this.boundHandleDocumentClick);
      this.documentClickListenerAdded = true;
    }
  }

  disconnectedCallback() {
    if (this.boundHandleDocumentClick) {
      document.removeEventListener("click", this.boundHandleDocumentClick);
    }
  }

  @api
  async loadCurrentUser() {
    try {
      // DBから現在のユーザー情報を取得
      const profileData = await getUserProfile({ userId: "user001" });
      if (profileData) {
        const profile = JSON.parse(profileData);
        this.currentUser = {
          id: profile.id || "user001",
          name: profile.name || "田中太郎",
          email: profile.email || "taro.tanaka@example.com",
          photo:
            profile.photos && profile.photos.length > 0
              ? profile.photos[0]
              : "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face"
        };
      } else {
        // プロフィールが見つからない場合はデフォルト値
        this.currentUser = {
          id: "user001",
          name: "田中太郎",
          email: "taro.tanaka@example.com",
          photo:
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face"
        };
      }
    } catch (error) {
      console.error("Current user loading error:", error);
      // エラー時はデフォルト値を使用
      this.currentUser = {
        id: "user001",
        name: "田中太郎",
        email: "taro.tanaka@example.com",
        photo:
          "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face"
      };
    }
  }

  toggleUserMenu(event) {
    console.log("toggleUserMenu called, current state:", this.showUserMenu);
    event.stopPropagation();
    this.showUserMenu = !this.showUserMenu;
    console.log("toggleUserMenu new state:", this.showUserMenu);
  }

  closeUserMenu() {
    this.showUserMenu = false;
  }

  handleMenuClick(event) {
    event.stopPropagation();
  }

  handleDocumentClick(event) {
    if (!this.showUserMenu) return;

    const userMenuContainer = this.template.querySelector(
      ".user-menu-container"
    );
    if (userMenuContainer && !userMenuContainer.contains(event.target)) {
      console.log("Closing menu due to outside click");
      this.showUserMenu = false;
    }
  }

  handleNavigateToSearch() {
    this.dispatchEvent(
      new CustomEvent("navigate", {
        detail: { page: "search" }
      })
    );
  }

  handleEditProfile() {
    console.log("handleEditProfile called");
    this.closeUserMenu();
    this.dispatchEvent(
      new CustomEvent("navigate", {
        detail: { page: "profile-edit", userId: this.currentUser.id }
      })
    );
    console.log("Navigate event dispatched for profile-edit");
  }

  handleViewProfile() {
    this.closeUserMenu();
    this.dispatchEvent(
      new CustomEvent("navigate", {
        detail: { page: "profile-view", userId: this.currentUser.id }
      })
    );
  }

  handleSettings() {
    this.closeUserMenu();
    this.dispatchEvent(
      new CustomEvent("navigate", {
        detail: { page: "settings" }
      })
    );
  }

  handleLogout() {
    this.closeUserMenu();
    // TODO: ログアウト処理を実装
    console.log("ログアウト処理");
    this.dispatchEvent(new CustomEvent("logout"));
  }

  get navButtonClass() {
    return "nav-button";
  }
}
