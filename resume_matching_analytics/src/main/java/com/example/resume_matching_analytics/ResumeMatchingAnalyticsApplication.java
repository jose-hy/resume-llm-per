package com.example.resume_matching_analytics;

import com.example.resume_matching_analytics.Analytics.AnalyticsConfig;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.FilterType;

@ComponentScan(excludeFilters = @ComponentScan.Filter(
		type = FilterType.ASSIGNABLE_TYPE,
		classes = AnalyticsConfig.class)
)
@SpringBootApplication()
public class ResumeMatchingAnalyticsApplication {

	public static void main(String[] args) {
		SpringApplication.run(ResumeMatchingAnalyticsApplication.class, args);
	}

}
