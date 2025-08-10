import { LightningElement, api, track } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

export default class UserProfileCard extends LightningElement {
    @api profileData = {};
    @api showMatchingActions = false; // マッチングアクション表示フラグ
    @api isOwnProfile = false; // 自分のプロフィールかどうか
    @api currentUserId; // 現在のユーザーID

    @track showDetails = false;

    // 計算プロパティ：メイン写真
    get mainPhoto() {
        return this.profileData.photos && this.profileData.photos.length > 0 
            ? this.profileData.photos[0] 
            : null;
    }

    // 計算プロパティ：写真があるかどうか
    get hasPhotos() {
        return this.profileData.photos && this.profileData.photos.length > 0;
    }

    // 計算プロパティ：趣味があるかどうか
    get hasInterests() {
        return this.profileData.interests && this.profileData.interests.length > 0;
    }

    // 計算プロパティ：オンライン状態
    get isOnline() {
        if (!this.profileData.lastActive) return false;
        
        const lastActive = new Date(this.profileData.lastActive);
        const now = new Date();
        const diffInMinutes = (now - lastActive) / (1000 * 60);
        
        return diffInMinutes <= 5; // 5分以内ならオンライン
    }

    // 計算プロパティ：詳細ボタンのラベル
    get detailsButtonLabel() {
        return this.showDetails ? '詳細を非表示' : '詳細を表示';
    }

    // 詳細表示切り替え
    toggleDetails() {
        this.showDetails = !this.showDetails;
    }

    // いいね処理
    handleLike() {
        this.dispatchCustomEvent('like', {
            targetUserId: this.profileData.id,
            action: 'like'
        });
        
        this.showToast('いいね！', `${this.profileData.name}にいいねを送りました`, 'success');
        
        // アニメーション効果
        this.addActionAnimation('like');
    }

    // パス処理
    handlePass() {
        this.dispatchCustomEvent('pass', {
            targetUserId: this.profileData.id,
            action: 'pass'
        });
        
        // アニメーション効果
        this.addActionAnimation('pass');
    }

    // スーパーいいね処理
    handleSuperLike() {
        this.dispatchCustomEvent('superlike', {
            targetUserId: this.profileData.id,
            action: 'superlike'
        });
        
        this.showToast('スーパーいいね！', `${this.profileData.name}にスーパーいいねを送りました`, 'success');
        
        // アニメーション効果
        this.addActionAnimation('superlike');
    }

    // 編集処理
    handleEdit() {
        this.dispatchCustomEvent('edit', {
            profileData: this.profileData
        });
    }

    // メッセージ処理
    handleMessage() {
        this.dispatchCustomEvent('message', {
            targetUserId: this.profileData.id,
            targetName: this.profileData.name
        });
    }

    // プロフィールクリック処理
    handleProfileClick() {
        this.dispatchCustomEvent('profileclick', {
            profileData: this.profileData
        });
    }

    // カスタムイベント発火ヘルパー
    dispatchCustomEvent(eventName, detail) {
        const event = new CustomEvent(eventName, {
            detail: detail,
            bubbles: true,
            composed: true
        });
        this.dispatchEvent(event);
    }

    // アクションアニメーション追加
    addActionAnimation(actionType) {
        const card = this.template.querySelector('.profile-card');
        if (card) {
            card.classList.add(`action-${actionType}`);
            
            // アニメーション終了後にクラスを削除
            setTimeout(() => {
                card.classList.remove(`action-${actionType}`);
            }, 600);
        }
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

    // プロフィールデータの更新（外部から呼び出し可能）
    @api
    updateProfile(newProfileData) {
        this.profileData = { ...newProfileData };
    }

    // カードの表示/非表示切り替え（外部から呼び出し可能）
    @api
    toggleVisibility() {
        const card = this.template.querySelector('.profile-card');
        if (card) {
            card.style.display = card.style.display === 'none' ? 'block' : 'none';
        }
    }

    // アクションの有効/無効切り替え（外部から呼び出し可能）
    @api
    setActionsEnabled(enabled) {
        const buttons = this.template.querySelectorAll('.action-btn, lightning-button');
        buttons.forEach(button => {
            button.disabled = !enabled;
        });
    }

    // 年齢計算ヘルパー（生年月日から年齢を計算する場合）
    calculateAge(birthDate) {
        if (!birthDate) return null;
        
        const today = new Date();
        const birth = new Date(birthDate);
        let age = today.getFullYear() - birth.getFullYear();
        const monthDiff = today.getMonth() - birth.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
            age--;
        }
        
        return age;
    }

    // 距離計算ヘルパー（将来の機能拡張用）
    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // 地球の半径（km）
        const dLat = this.toRadians(lat2 - lat1);
        const dLon = this.toRadians(lon2 - lon1);
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(this.toRadians(lat1)) * Math.cos(this.toRadians(lat2)) *
                  Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }

    toRadians(degrees) {
        return degrees * (Math.PI/180);
    }
}