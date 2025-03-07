package com.example.resume_matching_analytics.Analytics;

import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class AnalyticsConfig {
    @Bean
    CommandLineRunner commandLineRunner(AnalyticsRepository analyticsRepository) {
        return args -> {
            Analytics a = new Analytics("clicks");
            Analytics b = new Analytics("clicks");
            analyticsRepository.saveAll(List.of(
                    a, b
            ));
        };
    }

}

