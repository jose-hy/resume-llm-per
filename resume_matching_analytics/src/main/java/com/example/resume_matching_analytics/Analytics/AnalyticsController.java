package com.example.resume_matching_analytics.Analytics;

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping(path = "/analytics")
public class AnalyticsController {
    private final AnalyticsService analyticsService;

    @Autowired
    public AnalyticsController(AnalyticsService analyticsService) {
        this.analyticsService = analyticsService;
    }

    @GetMapping
    public List<Analytics> getAnalytics() {
        return analyticsService.getAnalytics();
    }

    @PostMapping("/appliedTo")
    public void appliedTo(@RequestBody Map<String, Object> payload) {
        analyticsService.updateAppliedTo(payload);
    }

    @PostMapping("/handleJobClickedOn")
    public void handleJobClickedOn(@RequestBody AddAnalyticsDTO payload, HttpServletRequest req) {
        analyticsService.initializeAnalytics(payload, req);
    }

    @PostMapping("/initializeAnalytics")
    public void initializeJobsViewed(@RequestBody AddAnalyticsDTO payload, HttpServletRequest req) {
        analyticsService.initializeAnalytics(payload, req);
    }

    @PutMapping("/updateJobsViewed")
    public void updateJobsViewed(@RequestBody Map<String, Object> payload) {
        analyticsService.updateJobsViewed(payload);
    }

    @DeleteMapping(path = "{analyticsId}")
    public void deleteAnalytics(@PathVariable("analyticsId") Long analyticsId) {
        analyticsService.deleteAnalytics(analyticsId);
    }
}

