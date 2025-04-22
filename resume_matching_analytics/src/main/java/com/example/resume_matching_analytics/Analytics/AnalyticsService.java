package com.example.resume_matching_analytics.Analytics;

import com.example.resume_matching_analytics.Auth.service.JWTService;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
public class AnalyticsService {
    private final AnalyticsRepository analyticsRepository;

    @Autowired
    private JWTService jwtService;

    @Autowired
    public AnalyticsService(AnalyticsRepository analyticsRepository) {
        this.analyticsRepository = analyticsRepository;
    }

    public List<Analytics> getAnalytics() {
        return analyticsRepository.findAllAnalytics();
    }

    public String getUsername(HttpServletRequest req) {
        String authHeader = req.getHeader("Authorization");
        Cookie[] cookies = req.getCookies();
        String username = null;
        String token = null;
        if (cookies != null) {
            for (Cookie cookie : cookies) {
                if ("accessCode".equals(cookie.getName())) {
                    token = cookie.getValue();
                    username = jwtService.extractUsername(token);
                }
            }
        }

        if (username == null && authHeader != null && authHeader.startsWith("Bearer ")) {
            token = authHeader.substring(7);
            username = jwtService.extractUsername(token);
        }

        return username;
    }

    public void initializeAnalytics(AddAnalyticsDTO payload, HttpServletRequest req) {
        String type = payload.getType();
        if (type.equals("dau")) {
            analyticsRepository.saveCustomOncePerDay(payload.getType(), payload.getData(), getUsername(req));
        } else {
            analyticsRepository.saveCustom(payload.getType(), payload.getData(), getUsername(req));
        }
    }

    public void updateAppliedTo(Map<String, Object> payload) {
        analyticsRepository.updateAppliedTo(payload.get("job_id"), payload.get("job_title"), payload.get("location"), payload.get("url"), payload.get("remote"));
    }

    public void updateJobsViewed(Map<String, Object> payload) {
        analyticsRepository.updateJobsViewed(payload.get("jobs_count"), payload.get("jobs_viewed"), payload.get("session_id"));
    }

    public void deleteAnalytics(Long analyticsId) {
        analyticsRepository.deleteById(analyticsId);
    }

    @Transactional
    public void updateAnalytics(Long analyticsId, String type) {
        Analytics analytics = analyticsRepository.findById(analyticsId).orElseThrow(() -> new IllegalStateException("Id does not exist"));
    }
}
