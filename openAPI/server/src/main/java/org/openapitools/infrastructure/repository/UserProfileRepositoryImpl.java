package org.openapitools.infrastructure.repository;

import org.openapitools.domain.entity.UserProfileEntity;
import org.openapitools.domain.repository.UserProfileDomainRepository;
import org.openapitools.domain.valueobject.UserId;
import org.openapitools.infrastructure.dto.UserProfileDataModel;
import org.openapitools.infrastructure.mapper.UserProfileInfrastructureMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * インフラストラクチャ層のリポジトリ実装
 * ドメイン↔データベース間の変換を担当
 * APIモデルに依存しないクリーンなアーキテクチャ
 */
@Repository
public class UserProfileRepositoryImpl implements UserProfileDomainRepository {
    
    @Autowired
    private UserProfileDataRepository dataRepository;
    
    @Autowired
    private UserProfileInfrastructureMapper infrastructureMapper;
    
    @Override
    public List<UserProfileEntity> findAllActive() {
        List<UserProfileDataModel> dataModels = dataRepository.selectAllActiveUserProfiles();
        return infrastructureMapper.dataModelListToDomainList(dataModels);
    }
    
    @Override
    public Optional<UserProfileEntity> findById(UserId userId) {
        UserProfileDataModel dataModel = dataRepository.selectUserProfileById(userId.getValue());
        if (dataModel != null) {
            return Optional.of(infrastructureMapper.dataModelToDomain(dataModel));
        }
        return Optional.empty();
    }
    
    @Override
    public UserProfileEntity save(UserProfileEntity entity) {
        UserProfileDataModel dataModel = infrastructureMapper.domainToDataModel(entity);
        dataRepository.insertUserProfile(dataModel);
        
        // 趣味と写真の挿入
        if (entity.getInterests() != null && !entity.getInterests().isEmpty()) {
            dataRepository.insertUserInterests(entity.getUserId().getValue(), 
                entity.getInterests());
        }
        if (entity.getPhotos() != null && !entity.getPhotos().isEmpty()) {
            dataRepository.insertUserPhotos(entity.getUserId().getValue(), 
                entity.getPhotos());
        }
        
        return entity;
    }
    
    @Override
    public UserProfileEntity update(UserProfileEntity entity) {
        UserProfileDataModel dataModel = infrastructureMapper.domainToDataModel(entity);
        dataRepository.updateUserProfile(dataModel);
        
        // 趣味と写真の更新
        String userId = entity.getUserId().getValue();
        dataRepository.deleteUserInterests(userId);
        dataRepository.deleteUserPhotos(userId);
        
        if (entity.getInterests() != null && !entity.getInterests().isEmpty()) {
            dataRepository.insertUserInterests(userId, entity.getInterests());
        }
        if (entity.getPhotos() != null && !entity.getPhotos().isEmpty()) {
            dataRepository.insertUserPhotos(userId, entity.getPhotos());
        }
        
        return entity;
    }
    
    @Override
    public void deleteById(UserId userId) {
        dataRepository.deleteUserProfile(userId.getValue());
    }
    
    @Override
    public List<UserProfileEntity> findBySearchCriteria(Integer minAge, Integer maxAge, 
                                                       String gender, String location, 
                                                       List<String> interests) {
        List<UserProfileDataModel> results = dataRepository.selectUserProfilesBySearch(
            minAge, maxAge, gender, location, interests);
        
        return infrastructureMapper.dataModelListToDomainList(results);
    }
    
    @Override
    public boolean existsById(UserId userId) {
        return dataRepository.existsUserProfileById(userId.getValue());
    }
}