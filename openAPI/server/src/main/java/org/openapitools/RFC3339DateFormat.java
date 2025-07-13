package org.openapitools;

import com.fasterxml.jackson.databind.util.StdDateFormat;

import java.text.DateFormat;
import java.text.FieldPosition;
import java.text.ParsePosition;
import java.util.Date;
import java.util.GregorianCalendar;
import java.util.TimeZone;

/**
 * RFC3339形式の日付文字列を処理するためのカスタムDateFormat実装を提供します。
 * RFC3339は、インターネットプロトコルやAPIで広く使用される日付と時刻の表現の標準であり、
 * 一貫性のある明確なタイムスタンプを保証します。
 *
 * このクラスの主な機能は次のとおりです。
 * - 日付の解析とフォーマットにおけるRFC3339仕様への準拠。
 * - 堅牢な日付処理のためのJacksonライブラリのStdDateFormatとの統合。
 * - デフォルトのタイムゾーンとしてUTC（協定世界時）を使用する構成。これは、サーバー側のアプリケーションで
 * タイムゾーン関連の問題を回避するための一般的な方法です。
 * - RFC3339標準の一部であるタイムゾーンオフセットにコロンを含めることのサポート。
 *
 * このクラスは、標準化された形式で日付オブジェクトをシリアライズおよびデシリアライズするために不可欠であり、
 * APIや分散システムでのデータの一貫性を確保するための重要なコンポーネントです。
 */
public class RFC3339DateFormat extends DateFormat {
  private static final long serialVersionUID = 1L;
  private static final TimeZone TIMEZONE_Z = TimeZone.getTimeZone("UTC");

  private final StdDateFormat fmt = new StdDateFormat()
      .withTimeZone(TIMEZONE_Z)
      .withColonInTimeZone(true);

  public RFC3339DateFormat() {
    this.calendar = new GregorianCalendar();
  }

  @Override
  public Date parse(String source, ParsePosition pos) {
    return fmt.parse(source, pos);
  }

  @Override
  public StringBuffer format(Date date, StringBuffer toAppendTo, FieldPosition fieldPosition) {
    return fmt.format(date, toAppendTo, fieldPosition);
  }

  @Override
  public Object clone() {
    return this;
  }
}
