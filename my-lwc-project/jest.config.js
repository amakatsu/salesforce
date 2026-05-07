/**
 * Jest 設定（@salesforce/sfdx-lwc-jest 公式パターン）。
 *
 * jestConfig が以下を提供する:
 *   - @lwc/jest-preset の transformer / serializer / setupFilesAfterEnv / testEnvironment(jsdom)
 *   - sfdx-lwc-jest 独自 resolver（"c/..." モジュール解決 / "@salesforce/apex/..." 仮想モジュール解決）
 *   - rootDir / collectCoverageFrom（force-app 配下を自動検出）
 *
 * package.json 内の jest 設定は本ファイルが優先されるため最小限に保つ。
 */
const { jestConfig } = require("@salesforce/sfdx-lwc-jest/config");

module.exports = {
  ...jestConfig,
  moduleDirectories: [
    "node_modules",
    "<rootDir>/force-app/main/default/lwc"
  ]
};
