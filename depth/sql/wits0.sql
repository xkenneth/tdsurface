alter table depth_wits0 add index depth_wits0_recid_itemid (recid, itemid, time_stamp, well_id);
alter table depth_wits0 add index depth_wits0_wellid_timestamp_recid_itemid (well_id, time_stamp, recid, itemid);
