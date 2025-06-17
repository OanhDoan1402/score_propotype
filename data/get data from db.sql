

--################################## USE 41 --##################################
---------------- LIST ORGANID FOR SAMPLE

-- ver 1
with base AS (
    select * from (select *, concat(Industry,'-',CompanySize) as ModelSegment
					from DA_test_new..hdn_scoring_yearly_sample order by OrganizationId,year_report) a
    where year_report = 2025 AND month_report = 4
),
ranked AS (
    select *,
        row_number() over (partition by ModelSegment order by Score desc) as rn_high,
        row_number() over (partition by ModelSegment order by Score asc) as rn_low,
        row_number() over (partition by ModelSegment order by case when Score = 0 then 999999 else Score end asc) as rn_low_nonzero
    from base
),
segment_sample AS (
    select OrganizationId, ModelSegment, 'HIGH_TOP50' as sample_type
        from ranked where rn_high <= 50

    UNION ALL

    select OrganizationId, ModelSegment, 'LOW_BOTTOM20' as sample_type
    from ranked where rn_low <= 20

    UNION ALL

    select OrganizationId, ModelSegment, 'LOW_NONZERO30' as sample_type
    from ranked where Score <> 0 AND rn_low_nonzero <= 30

-- ver 2

with segment as 
(select *, 
case when CompanySize in ('SME','MicroSME') then CONCAT(Industry,'-','MicroSME_SME')
	 when CompanySize = 'LargeCorp' then CONCAT(Industry,'-','LargeCorp')
	 else CONCAT(Industry,'-',CompanySize)
	 end as ModelSegment
from DA_test_new..hdn_scoring_yearly_sample 
),
CTE_FG_Distribution AS (
    SELECT OrganizationId,ModelSegment,FG,
        ROW_NUMBER() OVER (PARTITION BY ModelSegment, FG ORDER BY Score DESC) AS rn
    FROM segment
    WHERE year_report = 2025 AND month_report = 4 AND FG IS NOT NULL --and ModelSegment is not null
)
-- chọn ra 10 org cho mỗi FG x 18 x mỗi segment
, CTE_Organ_Selected AS (
    SELECT OrganizationId, ModelSegment
    FROM CTE_FG_Distribution
    WHERE rn <= 10
)
-- join lại bảng chính để lấy full thông tin
SELECT 
a.*
--distinct a.OrganizationId
FROM segment a
where year_report = 2025 AND month_report = 4 and OrganizationId in (select OrganizationId from CTE_Organ_Selected)
order by a.ModelSegment, FG






--################################## USE 133 --##################################
---------------- profile.csv

/* CODE TẠO BẢNG CHỨA LIST SAMPLE
drop table ##list_demo;
create table ##list_demo (OrganizationId int, ModelSegment nvarchar(500));

--		select * from ##list_demo


INSERT INTO ##list_demo (OrganizationId,ModelSegment) VALUES ('7597','Construction-LargeCorp');
*/

select distinct OrganizationId from ##list_demo --- 1440



select distinct t1.OrganizationId,
t2.TaxCode,
t3.en_ActiveStatusName,
t5.VSICCode,t5.VSICCodePath,t5.en_VSICName,
t5.VSICCode_LV3,t5.[en_VSICName (LV3)],
t2.en_OrganizationName,t2.OrganizationName,t2.Address,
t6.Ticker,
case when t7.TotalTradeCreditLimit is null then 'Not available' ELSE CAST(t7.TotalTradeCreditLimit AS VARCHAR) end as TotalTradeCreditLimit,
t1.Modelsegmentvsic,t1.Modelsegmentsize,t1.ModelSegment
from ##list_demo t1
left join FGFB_COIN_DR_OrganizationInformation t2 on t2.OrganizationId=t1.OrganizationId and t2.RecordStatusId=1 and t2.IsHistory=0
left join FGFB_COIN_DM_ActiveStatus t3 on t2.ActiveStatusId=t3.ActiveStatusId and t3.RecordStatusId=1 and t3.IsHistory=0
left join FGFB_COIN_DR_Organization_VSIC t4 on t1.OrganizationId=t4.OrganizationId and t4.RecordStatusId=1 and t4.IsHistory=0 and t4.IsMain=1
left join (
			select a.OrganizationId,b.VSICCode ,b.VSICCodePath, b.en_VSICName,
			c.VSICCode as 'VSICCode_LV3',c.en_VSICName as 'en_VSICName (LV3)'
			from FGFB_COIN_DR_Organization_VSIC a
			join FGFB_CMMS_DM_VSIC b on a.VSICId=b.VSICId and b.RecordStatusId=1 and b.IsHistory=0
			join FGFB_CMMS_DM_VSIC c on LEFT(b.VSICCodePath,8)=c.VSICCodePath and c.RecordStatusId=1 and c.IsHistory=0
			where a.RecordStatusId=1 and a.IsHistory=0 and a.IsMain=1
			) t5 on t1.OrganizationId=t5.OrganizationId
left join FGFB_COIN_DR_ListedInformation t6 on t1.OrganizationId=t6.OrganizationId and t6.RecordStatusId=1 and t6.IsHistory=0
left join  (
			select ScoreId, OrganizationId,PublicDateId, case when TotalTradeCreditLimit is null then 'Not available' ELSE CAST(TotalTradeCreditLimit AS VARCHAR) end as TotalTradeCreditLimit
			from (
				select a.ScoreId,a.OrganizationId,a.PublicDateId,b.TotalTradeCreditLimit,row_number() over (partition by a.OrganizationId order by a.PublicDateId desc, a.Priority asc) as RN
				from FGBI_GSRE_DR_Score a
				join FGBI_GSRE_DR_TotalTradeCreditLimit b on a.ScoreId=b.ScoreId and b.RecordStatusId=1 and b.IsHistory=0
				where a.RecordStatusId=1 and a.IsHistory=0 and a.ModelId=1
				) a where RN=1
) t7 on t1.OrganizationId=t7.OrganizationId




