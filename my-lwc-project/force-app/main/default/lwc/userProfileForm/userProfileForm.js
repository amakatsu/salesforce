import { LightningElement, track, api } from "lwc";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import saveUserProfile from "@salesforce/apex/UserProfileService.saveUserProfile";
import updateUserProfile from "@salesforce/apex/UserProfileService.updateUserProfile";
import getUserProfile from "@salesforce/apex/UserProfileService.getUserProfile";

export default class UserProfileForm extends LightningElement {
  @track formData = {
    name: "",
    age: 25,
    gender: "",
    location: "",
    bio: "",
    occupation: "",
    education: "",
    interests: [],
    lookingFor: "",
    ageRangeMin: 22,
    ageRangeMax: 35,
    maxDistance: 10,
    isActive: true
  };

  @api userId = null; // 外部から渡されるユーザーID
  @track selectedUserId = null; // 編集モードの場合
  @track isEditMode = false;
  @track isLoading = false;
  @track hasLoadAttempted = false;

  // 選択肢の定義
  genderOptions = [
    { label: "男性", value: "male" },
    { label: "女性", value: "female" },
    { label: "その他", value: "other" }
  ];

  educationOptions = [
    { label: "高校卒業", value: "高校卒業" },
    { label: "専門学校卒業", value: "専門学校卒業" },
    { label: "短期大学卒業", value: "短期大学卒業" },
    { label: "大学卒業", value: "大学卒業" },
    { label: "大学院卒業", value: "大学院卒業" }
  ];

  lookingForOptions = [
    { label: "友達", value: "友達" },
    { label: "恋人", value: "恋人" },
    { label: "結婚相手", value: "結婚相手" }
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

  // コンポーネント初期化時の処理
  connectedCallback() {
    if (this.userId) {
      this.loadUserProfile();
    }
  }

  // userIdプロパティが変更されたときの処理
  renderedCallback() {
    if (
      this.userId &&
      !this.isEditMode &&
      !this.isLoading &&
      !this.hasLoadAttempted
    ) {
      this.hasLoadAttempted = true;
      this.loadUserProfile();
    }

    // Shadow DOM内のtextareaに直接アクセスを試行
    this.tryDirectTextareaAccess();
  }

  // 直接textarea要素にアクセスしてスタイル適用を試行
  tryDirectTextareaAccess() {
    setTimeout(() => {
      console.log("Attempting direct textarea access...");
      const lightningTextareas =
        this.template.querySelectorAll("lightning-textarea");
      lightningTextareas.forEach((ltTextarea, index) => {
        console.log(`Lightning textarea ${index}:`, ltTextarea);
        console.log(`Shadow root:`, ltTextarea.shadowRoot);

        if (ltTextarea.shadowRoot) {
          const textarea = ltTextarea.shadowRoot.querySelector("textarea");
          if (textarea) {
            console.log("Found textarea, applying styles...");
            textarea.style.resize = "none";
            textarea.style.overflow = "hidden";
          }
        }
      });
    }, 100);
  }

  // ユーザープロフィールを読み込み
  async loadUserProfile() {
    if (!this.userId) return;

    this.isLoading = true;
    try {
      const profileData = await getUserProfile({ userId: this.userId });
      if (profileData) {
        this.loadProfile(JSON.parse(profileData));
      } else {
        // プロフィールが見つからない場合は新規作成モード
        this.selectedUserId = this.userId;
        this.isEditMode = false;
      }
    } catch (error) {
      console.error("プロフィール読み込みエラー:", error);
      // エラーの場合も新規作成モードとして続行
      this.isEditMode = false;
      this.selectedUserId = this.userId;
    } finally {
      this.isLoading = false;
    }
  }

  // 入力値変更処理
  handleInputChange(event) {
    const fieldName = event.target.name;
    const fieldValue = event.target.value;
    this.formData = { ...this.formData, [fieldName]: fieldValue };
  }

  // 趣味チェックボックス変更処理
  handleInterestChange(event) {
    const selectedValue = event.target.value;
    const isChecked = event.target.checked;

    // interestOptionsの状態を更新
    this.interestOptions = this.interestOptions.map((option) => {
      if (option.value === selectedValue) {
        return { ...option, checked: isChecked };
      }
      return option;
    });

    // formData.interestsを更新
    if (isChecked) {
      this.formData.interests = [...this.formData.interests, selectedValue];
    } else {
      this.formData.interests = this.formData.interests.filter(
        (interest) => interest !== selectedValue
      );
    }
  }

  // フォーム送信処理
  async handleSubmit(event) {
    event.preventDefault();

    try {
      // バリデーション
      if (!this.validateForm()) {
        return;
      }

      // 現在の日時を追加
      const profileData = {
        ...this.formData,
        createdDate: new Date().toISOString(),
        lastActive: new Date().toISOString()
      };

      let result;
      if (this.isEditMode && this.selectedUserId) {
        // 既存プロフィールを更新
        result = await updateUserProfile({
          userId: this.selectedUserId,
          profileData: profileData
        });
      } else {
        // 新規プロフィールを作成（userIdを含める）
        const profileWithId = {
          ...profileData,
          id: this.userId || this.selectedUserId || "user001"
        };
        result = await saveUserProfile({ profileData: profileWithId });
      }

      this.showToast(
        "成功",
        this.isEditMode
          ? "プロフィールを更新しました"
          : "プロフィールを作成しました",
        "success"
      );

      // フォームをリセット
      this.resetForm();

      // カスタムイベントを発火（親コンポーネントに通知）
      let parsedProfile = null;
      try {
        parsedProfile = result ? JSON.parse(result) : null;
      } catch (parseError) {
        console.error("JSON parse error:", parseError);
        parsedProfile = null;
      }

      this.dispatchEvent(
        new CustomEvent("profilesaved", {
          detail: {
            profile: parsedProfile,
            isEdit: this.isEditMode
          }
        })
      );
    } catch (error) {
      console.error("Profile save error:", error);
      let errorMessage = "プロフィールの保存に失敗しました";

      if (error.body && error.body.message) {
        errorMessage += ": " + error.body.message;
      } else if (error.message) {
        errorMessage += ": " + error.message;
      }

      this.showToast("エラー", errorMessage, "error");
    }
  }

  // バリデーション
  validateForm() {
    const requiredFields = ["name", "age", "gender", "location"];

    for (let field of requiredFields) {
      if (!this.formData[field]) {
        this.showToast(
          "エラー",
          "必須項目が入力されていません: " + this.getFieldLabel(field),
          "error"
        );
        return false;
      }
    }

    // 年齢範囲のバリデーション
    if (this.formData.ageRangeMin > this.formData.ageRangeMax) {
      this.showToast(
        "エラー",
        "希望年齢の最小値が最大値を上回っています",
        "error"
      );
      return false;
    }

    return true;
  }

  // フィールドラベル取得
  getFieldLabel(fieldName) {
    const labels = {
      name: "名前",
      age: "年齢",
      gender: "性別",
      location: "居住地"
    };
    return labels[fieldName] || fieldName;
  }

  // キャンセル処理
  handleCancel() {
    this.resetForm();
    this.dispatchEvent(new CustomEvent("cancel"));
  }

  // フォームリセット
  resetForm() {
    this.formData = {
      name: "",
      age: 25,
      gender: "",
      location: "",
      bio: "",
      occupation: "",
      education: "",
      interests: [],
      lookingFor: "",
      ageRangeMin: 22,
      ageRangeMax: 35,
      maxDistance: 10,
      isActive: true
    };

    // 趣味チェックボックスもリセット
    this.interestOptions = this.interestOptions.map((option) => ({
      ...option,
      checked: false
    }));

    this.isEditMode = false;
    this.selectedUserId = null;
  }

  // 編集モードでプロフィールデータをロード
  loadProfile(profileData) {
    this.formData = { ...profileData };
    this.isEditMode = true;
    this.selectedUserId = profileData.id;

    // 趣味チェックボックスの状態を更新
    this.interestOptions = this.interestOptions.map((option) => ({
      ...option,
      checked: profileData.interests.includes(option.value)
    }));
  }

  // トースト表示
  showToast(title, message, variant) {
    const evt = new ShowToastEvent({
      title: title,
      message: message,
      variant: variant
    });
    this.dispatchEvent(evt);
  }

  // 公開メソッド：外部から編集モードで呼び出し可能
  editProfile(profileData) {
    this.loadProfile(profileData);
  }
}
