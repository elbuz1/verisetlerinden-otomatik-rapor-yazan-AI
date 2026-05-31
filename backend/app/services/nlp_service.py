import random
from datetime import datetime
from typing import Optional


class NLPCommentGenerator:
    """
    Harici AI API kullanmadan, rule-based ve template-based
    dinamik yorum uretme motoru.

    Veri analiz sonuclarina gore farkli sablonlar secer,
    degiskenleri doldurur ve insan yazimi gibi raporlar olusturur.
    """

    def __init__(self):
        self._init_templates()

    def _init_templates(self):
        self.EXEC_SUMMARY_INTROS = [
            "Bu rapor, {row_count:,} satır ve {col_count} sütundan oluşan veri setinin kapsamlı analizini sunmaktadır.",
            "Toplam {row_count:,} kayıt içeren bu veri seti üzerinde gerçekleştirilen detaylı analiz sonuçları aşağıda özetlenmektedir.",
            "İncelenen veri seti {row_count:,} gözlem ve {col_count} değişken barındırmakta olup, analiz bulguları bu bölümde paylaşılmaktadır.",
            "{row_count:,} satırlık veri seti üzerinde yapılan istatistiksel analiz, dikkat çekici sonuçlar ortaya koymuştur.",
        ]

        self.QUALITY_COMMENTS = {
            "A": [
                "Veri kalitesi değerlendirmesi sonucunda veri seti '{grade}' ({label}) olarak sınıflandırılmıştır. Veri bütünlüğü oldukça yüksek düzeydedir.",
                "Veri seti mükemmel kalite skoruna sahiptir ({score}/100). Eksik veri oranı minimum düzeyde olup analiz güvenilirliği yüksektir.",
                "Kalite analizi, veri setinin üretim ortamında güvenle kullanılabileceğini göstermektedir. Genel skor: {score}/100.",
            ],
            "B": [
                "Veri kalitesi iyi düzeydedir (Skor: {score}/100). Bazı iyileştirmeler yapılarak analiz güvenilirliği artırılabilir.",
                "Genel veri kalitesi tatmin edici olmakla birlikte, belirli sütunlardaki eksik veriler dikkat gerektirmektedir.",
                "Veri seti '{grade}' kalite sınıfında yer almaktadır. Mevcut haliyle analize uygun olmakla birlikte, veri temizleme önerilir.",
            ],
            "C": [
                "Veri kalitesi orta düzeydedir (Skor: {score}/100). Analiz sonuçları yorumlanırken eksik veri oranı göz önünde bulundurulmalıdır.",
                "Dikkat: Veri setinde kayda değer kalite sorunları tespit edilmiştir. Sonuçlar bu kısıtlamalar çerçevesinde değerlendirilmelidir.",
            ],
            "D": [
                "Uyarı: Veri kalitesi düşük düzeydedir (Skor: {score}/100). Analiz sonuçlarının güvenilirliği sınırlıdır.",
                "Kritik: Veri setinde ciddi kalite sorunları mevcuttur. Karar alma süreçlerinde bu sonuçlara temkinli yaklaşılması önerilir.",
            ],
        }

        self.TREND_UP = [
            "{col} değişkeninde belirgin bir yükseliş trendi gözlemlenmektedir (eğim: {slope}, R²: {r2}).",
            "{col} sütunundaki veriler tutarlı bir artış eğilimi sergilemektedir. Bu trend istatistiksel olarak anlamlıdır (p={p_value}).",
            "Dikkat çekici bir bulgu olarak, {col} değerlerinin zaman içinde %{change} oranında arttığı tespit edilmiştir.",
            "{col} alanında süregelen bir büyüme dinamiği söz konusudur. Toplam değişim %{change} olup, bu durum stratejik açıdan olumlu değerlendirilmektedir.",
        ]

        self.TREND_DOWN = [
            "{col} değişkeninde düşüş trendi dikkat çekmektedir (eğim: {slope}, R²: {r2}).",
            "{col} sütunundaki değerler azalma eğilimindedir. Bu düşüş %{change} oranına ulaşmıştır.",
            "Risk göstergesi: {col} alanında istatistiksel olarak anlamlı bir gerileme tespit edilmiştir (p={p_value}).",
            "{col} metriğindeki düşüş trendi, önlem alınması gereken bir duruma işaret etmektedir. Gerileme oranı: %{change}.",
        ]

        self.TREND_STABLE = [
            "{col} değişkeni kararlı bir seyir izlemektedir; belirgin bir trend bulunmamaktadır.",
            "{col} sütunundaki değerler dengeli bir dağılım göstermekte olup, önemli bir değişim gözlemlenmemektedir.",
        ]

        self.CORRELATION_STRONG_POS = [
            "{col1} ve {col2} arasında güçlü bir pozitif korelasyon tespit edilmiştir (r={value}). Bu iki değişken birlikte artış gösterme eğilimindedir.",
            "Analiz sonuçları, {col1} ile {col2} arasında dikkat çekici bir doğrusal ilişki ortaya koymaktadır (r={value}). Bu bulgu, iki metriğin birbirini etkileyebileceğine işaret etmektedir.",
        ]

        self.CORRELATION_STRONG_NEG = [
            "{col1} ve {col2} arasında güçlü bir negatif korelasyon mevcuttur (r={value}). Biri artarken diğeri azalma eğilimindedir.",
            "Ters yönlü güçlü bir ilişki: {col1} arttıkça {col2} düşmektedir (r={value}). Bu durum, kaynakların yeniden dağılımına işaret edebilir.",
        ]

        self.ANOMALY_COMMENTS = [
            "{col} sütununda {count} adet anomali tespit edilmiştir ({percentage}%). Bu aykırı değerler, veri girişi hataları veya gerçek uç durumları yansıtıyor olabilir.",
            "Dikkat: {col} alanında normalden sapan {count} değer bulunmaktadır. Alt sınır: {lower}, Üst sınır: {upper}.",
            "{col} değişkenindeki aykırı değerler incelenmelidir. Tespit edilen {count} anomali, toplam verinin %{percentage}'ini oluşturmaktadır.",
        ]

        self.MISSING_DATA_COMMENTS = {
            "low": [
                "Eksik veri oranı kabul edilebilir düzeydedir (%{percentage}). Veri setinin bütünlüğü büyük ölçüde korunmaktadır.",
                "Minimal düzeyde eksik veri tespit edilmiştir (%{percentage}). Bu durum analiz güvenilirliğini olumsuz etkilememektedir.",
            ],
            "medium": [
                "Eksik veri oranı %{percentage} düzeyindedir. {worst_col} sütunu en yüksek eksik oranına sahiptir (%{worst_pct}). Veri tamamlama yöntemleri değerlendirilmelidir.",
                "Orta düzeyde eksik veri mevcuttur (%{percentage}). Özellikle {worst_col} alanındaki boşluklar, analiz sonuçlarını etkileyebilir.",
            ],
            "high": [
                "Uyarı: Yüksek oranda eksik veri tespit edilmiştir (%{percentage}). Bu durum analiz sonuçlarının güvenilirliğini ciddi ölçüde etkilemektedir.",
                "Kritik: Veri setinin %{percentage}'i eksiktir. {worst_col} sütunundaki %{worst_pct} eksik oran, bu alanın analizden çıkarılmasını gerektirebilir.",
            ],
        }

        self.DISTRIBUTION_COMMENTS = {
            "normal": [
                "{col} değişkeni normal dağılıma yakın bir profil sergilemektedir (p={p_value}). Parametrik istatistiksel testler güvenle uygulanabilir.",
            ],
            "right_skewed": [
                "{col} sütunu sağa çarpık bir dağılım göstermektedir (çarpıklık: {skewness}). Çoğu değer düşük aralıkta yoğunlaşırken, az sayıda yüksek değer dağılımı etkiemektedir.",
                "{col} alanındaki sağa çarpık dağılım, potansiyel aykırı değerlerin varlığına işaret etmektedir. Medyan bazlı analizler daha güvenilir sonuçlar verecektir.",
            ],
            "left_skewed": [
                "{col} değişkeni sola çarpık dağılım sergilemektedir (çarpıklık: {skewness}). Değerler yüksek aralıkta yoğunlaşma eğilimindedir.",
            ],
        }

        self.RECOMMENDATION_TEMPLATES = {
            "missing_data": [
                "Eksik veri oranı yüksek olan {col} sütunu için veri tamamlama (imputation) stratejisi uygulanması önerilir. Ortalama, medyan veya KNN tabanlı tamamlama yöntemleri değerlendirilmelidir.",
                "{col} alanındaki %{pct} eksik veri oranı, veri toplama süreçlerinin gözden geçirilmesini gerektirmektedir.",
            ],
            "anomaly": [
                "{col} sütunundaki aykırı değerler detaylı incelenmelidir. Hatalı veri girişlerinin düzeltilmesi, gerçek aykırı değerlerin ise ayrı bir segmentte değerlendirilmesi önerilir.",
                "Anomali tespiti sonuçlarına göre, {col} alanında veri doğrulama kurallarının güçlendirilmesi tavsiye edilmektedir.",
            ],
            "correlation": [
                "{col1} ve {col2} arasındaki güçlü korelasyon ({value}), çoklu regresyon modellerinde dikkatli olunmasını gerektirmektedir. Multikolinearite kontrolü yapılmalıdır.",
                "{col1}-{col2} ilişkisi stratejik karar alma süreçlerinde değerlendirilmelidir. Bu iki metriğin birlikte optimizasyonu, genel performansı artırabilir.",
            ],
            "trend_up": [
                "{col} alanındaki yükseliş trendi izlenmeye devam edilmelidir. Bu trendin sürdürülebilirliğinin değerlendirilmesi ve destekleyici aksiyonların planlanması önerilir.",
            ],
            "trend_down": [
                "{col} metriğindeki düşüş trendi acil müdahale gerektirebilir. Kök neden analizi yapılarak düzeltici aksiyonlar planlanmalıdır.",
                "{col} alanındaki gerilemenin nedenlerini araştırmak için derinlemesine analiz yapılması önerilmektedir.",
            ],
            "quality": [
                "Veri kalitesini artırmak için periyodik veri denetim süreçleri oluşturulmalıdır.",
                "Veri toplama formlarında zorunlu alan kontrollerinin güçlendirilmesi, eksik veri oranını azaltacaktır.",
            ],
        }

    def generate_executive_summary(self, analysis: dict, dataset_name: str) -> str:
        basic = analysis.get("basic_stats", {})
        quality = analysis.get("data_quality_score", {})
        missing = analysis.get("missing_data", {})
        trends = analysis.get("trend_analysis", {})
        anomalies = analysis.get("anomalies", {})
        correlations = analysis.get("correlation_matrix", {})

        sections = []

        intro = random.choice(self.EXEC_SUMMARY_INTROS).format(
            row_count=basic.get("total_rows", 0),
            col_count=basic.get("total_columns", 0),
        )
        sections.append(intro)

        grade = quality.get("grade", "C")
        templates = self.QUALITY_COMMENTS.get(grade, self.QUALITY_COMMENTS["C"])
        quality_comment = random.choice(templates).format(
            grade=grade, label=quality.get("label", ""), score=quality.get("overall", 0)
        )
        sections.append(quality_comment)

        up_trends = [k for k, v in trends.items() if v.get("direction") == "yukari" and v.get("is_significant")]
        down_trends = [k for k, v in trends.items() if v.get("direction") == "asagi" and v.get("is_significant")]

        if up_trends:
            if len(up_trends) == 1:
                sections.append(f"Öne çıkan bulgu olarak, {up_trends[0]} metriğinde istatistiksel olarak anlamlı bir yükseliş trendi tespit edilmiştir.")
            else:
                cols = ", ".join(up_trends[:3])
                sections.append(f"Pozitif gelişme: {cols} alanlarında anlamlı yükseliş trendleri gözlemlenmektedir.")

        if down_trends:
            if len(down_trends) == 1:
                sections.append(f"Dikkat gerektiren alan: {down_trends[0]} metriğinde düşüş trendi belirlenmiştir.")
            else:
                cols = ", ".join(down_trends[:3])
                sections.append(f"Risk alanları: {cols} metriklerinde gerileme eğilimi söz konusudur.")

        total_anomalies = anomalies.get("total_anomalies", 0)
        if total_anomalies > 0:
            anomaly_cols = list(anomalies.get("by_column", {}).keys())
            if anomaly_cols:
                sections.append(
                    f"Anomali tespiti sonucunda toplam {total_anomalies} aykırı değer belirlenmiştir. "
                    f"En çok anomali içeren alanlar: {', '.join(anomaly_cols[:3])}."
                )

        strong_corrs = correlations.get("strong_correlations", [])
        if strong_corrs:
            top = strong_corrs[0]
            sections.append(
                f"Korelasyon analizinde en dikkat çekici bulgu, {top['column1']} ile {top['column2']} "
                f"arasındaki {'pozitif' if top['value'] > 0 else 'negatif'} ilişkidir (r={top['value']})."
            )

        missing_pct = missing.get("missing_percentage", 0)
        if missing_pct > 5:
            sections.append(
                f"Veri setinde %{missing_pct} oranında eksik veri bulunmaktadır. "
                f"Bu durum, analiz sonuçlarının yorumlanmasında dikkate alınmalıdır."
            )

        return "\n\n".join(sections)

    def generate_trend_comments(self, trends: dict) -> list[dict]:
        comments = []
        for col, trend in trends.items():
            direction = trend.get("direction", "yatay")
            change = abs(trend.get("overall_change_percent", 0))
            slope = trend.get("slope", 0)
            r2 = trend.get("r_squared", 0)
            p_value = trend.get("p_value", 1)

            if direction == "yukari":
                template = random.choice(self.TREND_UP)
            elif direction == "asagi":
                template = random.choice(self.TREND_DOWN)
            else:
                template = random.choice(self.TREND_STABLE)

            comment = template.format(
                col=col, slope=round(slope, 4), r2=round(r2, 4),
                change=round(change, 2), p_value=round(p_value, 4),
            )
            comments.append({
                "column": col,
                "direction": direction,
                "comment": comment,
                "significance": "yuksek" if p_value < 0.01 else "orta" if p_value < 0.05 else "dusuk",
            })

        return comments

    def generate_correlation_comments(self, correlations: dict) -> list[dict]:
        comments = []
        for corr in correlations.get("strong_correlations", []):
            if corr["value"] > 0:
                template = random.choice(self.CORRELATION_STRONG_POS)
            else:
                template = random.choice(self.CORRELATION_STRONG_NEG)

            comment = template.format(
                col1=corr["column1"], col2=corr["column2"], value=corr["value"],
            )
            comments.append({
                "columns": [corr["column1"], corr["column2"]],
                "value": corr["value"],
                "comment": comment,
            })

        return comments

    def generate_anomaly_comments(self, anomalies: dict) -> list[dict]:
        comments = []
        for col, info in anomalies.get("by_column", {}).items():
            template = random.choice(self.ANOMALY_COMMENTS)
            comment = template.format(
                col=col,
                count=info["iqr_outlier_count"],
                percentage=info["iqr_outlier_percentage"],
                lower=info["lower_bound"],
                upper=info["upper_bound"],
            )
            comments.append({
                "column": col,
                "severity": info["severity"],
                "comment": comment,
            })

        return comments

    def generate_missing_data_comments(self, missing: dict) -> str:
        pct = missing.get("missing_percentage", 0)
        columns_info = missing.get("columns_with_missing", {})

        if pct == 0:
            return "Veri setinde herhangi bir eksik değer bulunmamaktadır. Tüm hücreler eksiksiz doldurulmuştur."

        worst_col = max(columns_info.keys(), key=lambda k: columns_info[k]["percentage"]) if columns_info else "bilinmiyor"
        worst_pct = columns_info[worst_col]["percentage"] if worst_col in columns_info else 0

        if pct < 3:
            level = "low"
        elif pct < 15:
            level = "medium"
        else:
            level = "high"

        template = random.choice(self.MISSING_DATA_COMMENTS[level])
        return template.format(percentage=round(pct, 2), worst_col=worst_col, worst_pct=round(worst_pct, 2))

    def generate_distribution_comments(self, distributions: dict) -> list[dict]:
        comments = []
        for col, info in distributions.items():
            if info.get("is_normal"):
                template = random.choice(self.DISTRIBUTION_COMMENTS["normal"])
            elif info.get("skew_direction") == "saga_carpik":
                template = random.choice(self.DISTRIBUTION_COMMENTS["right_skewed"])
            elif info.get("skew_direction") == "sola_carpik":
                template = random.choice(self.DISTRIBUTION_COMMENTS["left_skewed"])
            else:
                continue

            comment = template.format(
                col=col,
                p_value=info.get("normality_p_value", 0),
                skewness=info.get("skewness", 0),
            )
            comments.append({"column": col, "comment": comment})

        return comments

    def generate_recommendations(self, analysis: dict) -> list[dict]:
        recs = []
        priority = 1

        missing = analysis.get("missing_data", {})
        for col, info in missing.get("columns_with_missing", {}).items():
            if info["percentage"] > 10:
                template = random.choice(self.RECOMMENDATION_TEMPLATES["missing_data"])
                recs.append({
                    "priority": priority,
                    "category": "Veri Kalitesi",
                    "recommendation": template.format(col=col, pct=info["percentage"]),
                })
                priority += 1

        anomalies = analysis.get("anomalies", {})
        for col, info in anomalies.get("by_column", {}).items():
            if info["severity"] in ["orta", "yuksek"]:
                template = random.choice(self.RECOMMENDATION_TEMPLATES["anomaly"])
                recs.append({
                    "priority": priority,
                    "category": "Anomali Yönetimi",
                    "recommendation": template.format(col=col),
                })
                priority += 1

        correlations = analysis.get("correlation_matrix", {})
        for corr in correlations.get("strong_correlations", [])[:3]:
            template = random.choice(self.RECOMMENDATION_TEMPLATES["correlation"])
            recs.append({
                "priority": priority,
                "category": "İlişki Analizi",
                "recommendation": template.format(
                    col1=corr["column1"], col2=corr["column2"], value=corr["value"]
                ),
            })
            priority += 1

        trends = analysis.get("trend_analysis", {})
        for col, trend in trends.items():
            if trend.get("is_significant") and trend.get("direction") == "asagi":
                template = random.choice(self.RECOMMENDATION_TEMPLATES["trend_down"])
                recs.append({
                    "priority": priority,
                    "category": "Trend Uyarısı",
                    "recommendation": template.format(col=col),
                })
                priority += 1

        for col, trend in trends.items():
            if trend.get("is_significant") and trend.get("direction") == "yukari":
                template = random.choice(self.RECOMMENDATION_TEMPLATES["trend_up"])
                recs.append({
                    "priority": priority,
                    "category": "Büyüme Fırsatı",
                    "recommendation": template.format(col=col),
                })
                priority += 1

        quality = analysis.get("data_quality_score", {})
        if quality.get("overall", 100) < 80:
            template = random.choice(self.RECOMMENDATION_TEMPLATES["quality"])
            recs.append({
                "priority": priority,
                "category": "Veri Yönetimi",
                "recommendation": template,
            })

        return sorted(recs, key=lambda x: x["priority"])

    def generate_all_comments(self, analysis: dict, dataset_name: str) -> dict:
        return {
            "executive_summary": self.generate_executive_summary(analysis, dataset_name),
            "trend_comments": self.generate_trend_comments(analysis.get("trend_analysis", {})),
            "correlation_comments": self.generate_correlation_comments(
                analysis.get("correlation_matrix", {})
            ),
            "anomaly_comments": self.generate_anomaly_comments(analysis.get("anomalies", {})),
            "missing_data_comment": self.generate_missing_data_comments(analysis.get("missing_data", {})),
            "distribution_comments": self.generate_distribution_comments(
                analysis.get("distribution_info", {})
            ),
            "recommendations": self.generate_recommendations(analysis),
            "generated_at": datetime.now().isoformat(),
            "report_language": "tr",
        }


nlp_service = NLPCommentGenerator()
