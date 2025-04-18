package com.example.resume_matching_analytics.Analytics;

import jakarta.transaction.Transactional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AnalyticsRepository extends JpaRepository<Analytics, Long> {
    @Query(value = "SELECT * FROM analytics", nativeQuery = true)
    List<Analytics> findAllAnalytics();

    @Modifying
    @Transactional
    @Query(value = "INSERT INTO analytics (type, data, username) VALUES (:type, CAST(:data as JSONB), :username)", nativeQuery = true)
    void saveCustom(@Param("type") String type, @Param("data") String data, @Param("username") String username);

    @Modifying
    @Transactional
    @Query(value = "INSERT INTO analytics (type, data, username) SELECT :type, CAST(:data as JSONB), :username where not exists (select 1 from analytics where timestamp > date_trunc('day', timestamp) and timestamp < (date_trunc('day', timestamp) + interval '1 day' - interval '1 second') and username = :username and type = 'dau');", nativeQuery = true)
    void saveCustomOncePerDay(@Param("type") String type, @Param("data") String data, @Param("username") String username);

    @Modifying
    @Transactional
    @Query(value = "insert into analytics (username, data, type) values (:username, CAST(:data as JSONB), :type) on conflict (username, (data->>'session_id'), type) do update set data = jsonb_set(analytics.data, '{value}', true::text::jsonb);", nativeQuery = true)
    void atLeastOneJobSelected(@Param("username") String username, @Param("data") String data, @Param("type") String type);

    @Modifying
    @Transactional
    @Query(value = "UPDATE analytics SET data = data || jsonb_build_object('viewed', to_jsonb((data->>'viewed')::int4+ :jobs_count), 'clicked_on', to_jsonb((data->>'clicked_on')::int4 + :jobs_viewed)) where data->>'session_id' = :session_id and type = 'jobs_viewed';", nativeQuery = true)
    void updateJobsViewed(@Param("jobs_count") Object jobs_count, @Param("jobs_viewed") Object jobs_viewed, @Param("session_id") Object session_id);

    @Modifying
    @Transactional
    @Query(value = "INSERT INTO applied_to (job_id, job_title, location, url, remote) values (:job_id, :job_title, :location, :url, :remote) ON CONFLICT (job_id, job_title) DO UPDATE SET count = applied_to.count + 1;", nativeQuery = true)
    void updateAppliedTo(@Param("job_id") Object job_id, @Param("job_title") Object job_title, @Param("location") Object location, @Param("url") Object url, @Param("remote") Object remote);
}


