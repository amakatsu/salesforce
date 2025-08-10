import { LightningElement, track, wire, api } from "lwc";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import getAllUserProfiles from "@salesforce/apex/UserProfileService.getAllUserProfiles";
import searchUserProfiles from "@salesforce/apex/UserProfileService.searchUserProfiles";

export default class UserProfileList extends LightningElement {
  @track profiles = [];
  @track filteredProfiles = [];
  @track isLoading = false;
  @track hasError = false;
  @track errorMessage = "";
  @track showFilters = false;
  @track isCardView = true;
  @track showMatchingActions = true;
  @track currentUserId = "current-user"; // 実際の実装では動的に取得

  // 検索条件
  @track searchCriteria = {
    minAge: 18,
    maxAge: 50,
    gender: "",
    location: "",
    interests: []
  };

  // フィルターオプション
  genderOptions = [
    { label: "すべて", value: "" },
    { label: "男性", value: "male" },
    { label: "女性", value: "female" },
    { label: "その他", value: "other" }
  ];

  @track interestOptions = [
    { label: "映画", value: "映画", checked: false },
    { label: "音楽", value: "音楽", checked: false },
    { label: "料理", value: "料理", checked: false },
    { label: "旅行", value: "旅行", checked: false },
    { label: "スポーツ", value: "スポーツ", checked: false },
    { label: "読書", value: "読書", checked: false },
    { label: "ゲーム", value: "ゲーム", checked: false },
    { label: "アート", value: "アート", checked: false },
    { label: "アウトドア", value: "アウトドア", checked: false },
    { label: "カフェ巡り", value: "カフェ巡り", checked: false },
    { label: "ペット", value: "ペット", checked: false },
    { label: "写真", value: "写真", checked: false }
  ];

  // 初期化
  connectedCallback() {
    this.loadProfiles();
  }

  // プロフィール読み込み
  async loadProfiles() {
    this.isLoading = true;
    this.hasError = false;

    try {
      const result = await getAllUserProfiles();
      const profilesData = JSON.parse(result);

      this.profiles = profilesData.map((profile) => ({
        ...profile,
        isOwn: profile.id === this.currentUserId,
        firstPhoto: this.getFirstPhoto(profile.photos)
      }));

      this.applyFilters();
    } catch (error) {
      this.hasError = true;
      this.errorMessage = error.body ? error.body.message : error.message;
      this.showToast("エラー", "プロフィールの読み込みに失敗しました", "error");
    } finally {
      this.isLoading = false;
    }
  }

  // 検索実行
  async performSearch() {
    if (this.hasActiveFilters) {
      this.isLoading = true;

      try {
        const searchCriteriaWithInterests = {
          ...this.searchCriteria,
          interests: this.selectedInterests
        };

        const result = await searchUserProfiles({
          searchCriteria: JSON.stringify(searchCriteriaWithInterests)
        });
        const profilesData = JSON.parse(result);

        this.profiles = profilesData.map((profile) => ({
          ...profile,
          isOwn: profile.id === this.currentUserId,
          firstPhoto: this.getFirstPhoto(profile.photos)
        }));

        this.applyFilters();
      } catch (error) {
        this.hasError = true;
        this.errorMessage = error.body ? error.body.message : error.message;
        this.showToast("エラー", "検索に失敗しました", "error");
      } finally {
        this.isLoading = false;
      }
    } else {
      this.loadProfiles();
    }
  }

  // フィルター適用
  applyFilters() {
    this.filteredProfiles = this.profiles.filter((profile) => {
      // 年齢フィルター
      if (
        this.searchCriteria.minAge &&
        profile.age < this.searchCriteria.minAge
      )
        return false;
      if (
        this.searchCriteria.maxAge &&
        profile.age > this.searchCriteria.maxAge
      )
        return false;

      // 性別フィルター
      if (
        this.searchCriteria.gender &&
        profile.gender !== this.searchCriteria.gender
      )
        return false;

      // 居住地フィルター
      if (
        this.searchCriteria.location &&
        !profile.location
          .toLowerCase()
          .includes(this.searchCriteria.location.toLowerCase())
      )
        return false;

      // 趣味フィルター
      if (this.selectedInterests.length > 0) {
        const hasCommonInterest =
          profile.interests &&
          profile.interests.some((interest) =>
            this.selectedInterests.includes(interest)
          );
        if (!hasCommonInterest) return false;
      }

      return true;
    });
  }

  // 計算プロパティ
  get hasProfiles() {
    return this.filteredProfiles && this.filteredProfiles.length > 0;
  }

  get profilesCount() {
    return this.filteredProfiles ? this.filteredProfiles.length : 0;
  }

  get isListView() {
    return !this.isCardView;
  }

  get cardViewVariant() {
    return this.isCardView ? "brand" : "neutral";
  }

  get listViewVariant() {
    return this.isListView ? "brand" : "neutral";
  }

  get selectedInterests() {
    return this.interestOptions
      .filter((option) => option.checked)
      .map((option) => option.value);
  }

  get hasActiveFilters() {
    return (
      this.searchCriteria.minAge > 18 ||
      this.searchCriteria.maxAge < 50 ||
      this.searchCriteria.gender ||
      this.searchCriteria.location ||
      this.selectedInterests.length > 0
    );
  }

  // プロフィール写真の最初の画像を取得するヘルパー
  getFirstPhoto(photos) {
    return photos && photos.length > 0 ? photos[0] : null;
  }

  // イベントハンドラー
  handleSearch() {
    this.performSearch();
  }

  handleRefresh() {
    this.loadProfiles();
  }

  toggleFilters() {
    this.showFilters = !this.showFilters;
  }

  handleFilterChange(event) {
    const fieldName = event.target.name;
    const fieldValue = event.target.value;
    this.searchCriteria = { ...this.searchCriteria, [fieldName]: fieldValue };
  }

  handleInterestFilterChange(event) {
    const selectedValue = event.target.value;
    const isChecked = event.target.checked;

    this.interestOptions = this.interestOptions.map((option) => {
      if (option.value === selectedValue) {
        return { ...option, checked: isChecked };
      }
      return option;
    });
  }

  resetFilters() {
    this.searchCriteria = {
      minAge: 18,
      maxAge: 50,
      gender: "",
      location: "",
      interests: []
    };

    this.interestOptions = this.interestOptions.map((option) => ({
      ...option,
      checked: false
    }));

    this.loadProfiles();
  }

  // 表示モード切り替え
  setCardView() {
    this.isCardView = true;
  }

  setListView() {
    this.isCardView = false;
  }

  // プロフィールアクションハンドラー
  handleProfileLike(event) {
    const profileId =
      event.detail.targetUserId || event.target.dataset.profileId;
    const profile = this.profiles.find((p) => p.id === profileId);

    if (profile) {
      this.showToast(
        "いいね！",
        `${profile.name}にいいねを送りました`,
        "success"
      );
      // TODO: APIにいいね情報を送信
    }
  }

  handleProfilePass(event) {
    const profileId = event.detail.targetUserId;
    // TODO: パス処理のロジック
    this.removeProfileFromList(profileId);
  }

  handleProfileSuperLike(event) {
    const profileId = event.detail.targetUserId;
    const profile = this.profiles.find((p) => p.id === profileId);

    if (profile) {
      this.showToast(
        "スーパーいいね！",
        `${profile.name}にスーパーいいねを送りました`,
        "success"
      );
      // TODO: APIにスーパーいいね情報を送信
    }
  }

  handleProfileEdit(event) {
    const profileData = event.detail.profileData;
    // TODO: プロフィール編集モーダルを開く
    this.dispatchEvent(
      new CustomEvent("editprofile", {
        detail: { profileData }
      })
    );
  }

  handleProfileMessage(event) {
    const targetUserId = event.detail.targetUserId;
    const targetName = event.detail.targetName;
    // TODO: メッセージ画面を開く
    this.dispatchEvent(
      new CustomEvent("openmessage", {
        detail: { targetUserId, targetName }
      })
    );
  }

  handleProfileClick(event) {
    const profileId =
      event.detail.profileData?.id || event.target.dataset.profileId;
    const profileData = this.profiles.find((p) => p.id === profileId);

    if (profileData) {
      // TODO: プロフィール詳細モーダルを開く
      this.dispatchEvent(
        new CustomEvent("viewprofile", {
          detail: { profileData }
        })
      );
    }
  }

  // ヘルパーメソッド
  removeProfileFromList(profileId) {
    this.profiles = this.profiles.filter((profile) => profile.id !== profileId);
    this.applyFilters();
  }

  showToast(title, message, variant) {
    const evt = new ShowToastEvent({
      title: title,
      message: message,
      variant: variant
    });
    this.dispatchEvent(evt);
  }

  // 公開メソッド
  @api
  refreshProfiles() {
    this.loadProfiles();
  }

  @api
  addProfile(profileData) {
    this.profiles = [...this.profiles, profileData];
    this.applyFilters();
  }

  @api
  updateProfile(profileId, updatedData) {
    this.profiles = this.profiles.map((profile) => {
      if (profile.id === profileId) {
        return { ...profile, ...updatedData };
      }
      return profile;
    });
    this.applyFilters();
  }
}
